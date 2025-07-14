import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
from web3 import Web3
from web3.exceptions import BlockNotFound, TransactionNotFound
from config.config import Config

logger = logging.getLogger(__name__)

@dataclass
class UpgradeEvent:
    """Data class for protocol upgrade events."""
    protocol_name: str
    contract_address: str
    network: str
    event_type: str  # 'governance_proposal', 'implementation_upgrade', 'parameter_change'
    timestamp: datetime
    block_number: int
    transaction_hash: str
    description: str
    risk_score: float
    metadata: Dict[str, Any]

@dataclass
class GovernanceProposal:
    """Data class for governance proposals."""
    proposal_id: str
    title: str
    description: str
    proposer: str
    voting_start: datetime
    voting_end: datetime
    votes_for: int
    votes_against: int
    votes_abstain: int
    status: str  # 'pending', 'active', 'succeeded', 'failed', 'executed'
    execution_eta: Optional[datetime]
    risk_assessment: Dict[str, Any]

class BlockchainClient:
    """Client for interacting with multiple blockchain networks."""
    
    def __init__(self):
        self.config = Config()
        self.networks = {}
        self.session = None
        self.initialize_networks()
    
    def initialize_networks(self):
        """Initialize Web3 connections for all supported networks."""
        for network_name, network_config in self.config.NETWORKS.items():
            try:
                w3 = Web3(Web3.HTTPProvider(network_config['rpc_url']))
                if w3.is_connected():
                    self.networks[network_name] = {
                        'web3': w3,
                        'config': network_config
                    }
                    logger.info(f"Connected to {network_name}")
                else:
                    logger.error(f"Failed to connect to {network_name}")
            except Exception as e:
                logger.error(f"Error connecting to {network_name}: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_contract_events(self, network: str, contract_address: str, 
                                event_signature: str, from_block: int = 0, 
                                to_block: str = 'latest') -> List[Dict]:
        """Get events from a smart contract."""
        if network not in self.networks:
            raise ValueError(f"Network {network} not supported")
        
        w3 = self.networks[network]['web3']
        
        try:
            # Get contract ABI from explorer API
            contract_abi = await self._get_contract_abi(network, contract_address)
            contract = w3.eth.contract(address=contract_address, abi=contract_abi)
            
            # Get events
            events = []
            event_filter = contract.events[event_signature].create_filter(
                fromBlock=from_block, toBlock=to_block
            )
            
            for event in event_filter.get_all_entries():
                events.append({
                    'block_number': event.blockNumber,
                    'transaction_hash': event.transactionHash.hex(),
                    'event_data': dict(event.args),
                    'timestamp': await self._get_block_timestamp(network, event.blockNumber)
                })
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting contract events: {e}")
            return []
    
    async def _get_contract_abi(self, network: str, contract_address: str) -> List[Dict]:
        """Get contract ABI from blockchain explorer."""
        network_config = self.networks[network]['config']
        
        params = {
            'module': 'contract',
            'action': 'getabi',
            'address': contract_address,
            'apikey': network_config['api_key']
        }
        
        try:
            async with self.session.get(network_config['explorer_api'], params=params) as response:
                data = await response.json()
                if data['status'] == '1':
                    return json.loads(data['result'])
                else:
                    logger.error(f"Failed to get ABI for {contract_address}: {data.get('message', 'Unknown error')}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching ABI: {e}")
            return []
    
    async def _get_block_timestamp(self, network: str, block_number: int) -> datetime:
        """Get timestamp for a block."""
        w3 = self.networks[network]['web3']
        
        try:
            block = w3.eth.get_block(block_number)
            return datetime.fromtimestamp(block.timestamp)
        except BlockNotFound:
            logger.error(f"Block {block_number} not found")
            return datetime.now()
    
    async def get_governance_proposals(self, network: str, governance_address: str) -> List[GovernanceProposal]:
        """Get governance proposals for a protocol."""
        proposals = []
        
        try:
            # This is a simplified implementation - in reality, each governance system
            # (Compound, Aave, etc.) has different interfaces
            events = await self.get_contract_events(
                network, governance_address, 'ProposalCreated'
            )
            
            for event in events:
                proposal = GovernanceProposal(
                    proposal_id=str(event['event_data'].get('proposalId', 0)),
                    title=event['event_data'].get('description', '').split('\n')[0],
                    description=event['event_data'].get('description', ''),
                    proposer=event['event_data'].get('proposer', ''),
                    voting_start=event['timestamp'],
                    voting_end=event['timestamp'] + timedelta(days=3),  # Default 3 days
                    votes_for=0,
                    votes_against=0,
                    votes_abstain=0,
                    status='pending',
                    execution_eta=None,
                    risk_assessment={}
                )
                proposals.append(proposal)
            
            return proposals
            
        except Exception as e:
            logger.error(f"Error getting governance proposals: {e}")
            return []
    
    async def monitor_upgrade_events(self, network: str, protocol_addresses: List[str]) -> List[UpgradeEvent]:
        """Monitor protocol upgrade events across multiple contracts."""
        upgrade_events = []
        
        for address in protocol_addresses:
            try:
                # Monitor common upgrade events
                upgrade_signatures = [
                    'Upgraded',
                    'AdminChanged',
                    'ProxyUpgraded',
                    'ImplementationUpgraded'
                ]
                
                for signature in upgrade_signatures:
                    events = await self.get_contract_events(
                        network, address, signature, 
                        from_block=await self._get_recent_block(network)
                    )
                    
                    for event in events:
                        upgrade_event = UpgradeEvent(
                            protocol_name=await self._get_protocol_name(network, address),
                            contract_address=address,
                            network=network,
                            event_type='implementation_upgrade',
                            timestamp=event['timestamp'],
                            block_number=event['block_number'],
                            transaction_hash=event['transaction_hash'],
                            description=f"Contract upgrade detected: {signature}",
                            risk_score=await self._calculate_upgrade_risk(event),
                            metadata=event['event_data']
                        )
                        upgrade_events.append(upgrade_event)
                
            except Exception as e:
                logger.error(f"Error monitoring upgrades for {address}: {e}")
        
        return upgrade_events
    
    async def _get_recent_block(self, network: str, hours_back: int = 24) -> int:
        """Get block number from specified hours ago."""
        w3 = self.networks[network]['web3']
        current_block = w3.eth.block_number
        
        # Approximate blocks per hour (varies by network)
        blocks_per_hour = {
            'ethereum': 300,   # ~12 second blocks
            'polygon': 1800,   # ~2 second blocks
            'arbitrum': 1200   # ~1 second blocks
        }
        
        blocks_back = blocks_per_hour.get(network, 300) * hours_back
        return max(0, current_block - blocks_back)
    
    async def _get_protocol_name(self, network: str, address: str) -> str:
        """Get protocol name from contract address."""
        # This would typically involve looking up the contract in a database
        # or using a contract registry service
        return f"Protocol_{address[:8]}"
    
    async def _calculate_upgrade_risk(self, event: Dict) -> float:
        """Calculate risk score for an upgrade event."""
        # Simplified risk calculation - would be more sophisticated in production
        base_risk = 0.5
        
        # Factors that increase risk
        if 'admin' in str(event).lower():
            base_risk += 0.2
        if 'proxy' in str(event).lower():
            base_risk += 0.1
        
        return min(1.0, base_risk)
    
    async def get_transaction_details(self, network: str, tx_hash: str) -> Dict:
        """Get detailed transaction information."""
        if network not in self.networks:
            raise ValueError(f"Network {network} not supported")
        
        w3 = self.networks[network]['web3']
        
        try:
            tx = w3.eth.get_transaction(tx_hash)
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                'hash': tx_hash,
                'from': tx['from'],
                'to': tx['to'],
                'value': w3.from_wei(tx['value'], 'ether'),
                'gas_used': receipt['gasUsed'],
                'gas_price': w3.from_wei(tx['gasPrice'], 'gwei'),
                'status': receipt['status'],
                'block_number': receipt['blockNumber'],
                'logs': receipt['logs']
            }
            
        except TransactionNotFound:
            logger.error(f"Transaction {tx_hash} not found")
            return {}
        except Exception as e:
            logger.error(f"Error getting transaction details: {e}")
            return {}
    
    async def get_protocol_tvl(self, network: str, protocol_address: str) -> float:
        """Get Total Value Locked for a protocol."""
        # This would integrate with DeFi analytics APIs like DeFiLlama
        # For now, return a placeholder value
        return 1000000.0
    
    async def get_network_status(self, network: str) -> Dict:
        """Get network status and metrics."""
        if network not in self.networks:
            raise ValueError(f"Network {network} not supported")
        
        w3 = self.networks[network]['web3']
        
        try:
            latest_block = w3.eth.get_block('latest')
            
            return {
                'network': network,
                'chain_id': w3.eth.chain_id,
                'latest_block': latest_block.number,
                'block_time': latest_block.timestamp,
                'gas_price': w3.from_wei(w3.eth.gas_price, 'gwei'),
                'is_connected': w3.is_connected()
            }
            
        except Exception as e:
            logger.error(f"Error getting network status: {e}")
            return {}
    
    def get_supported_networks(self) -> List[str]:
        """Get list of supported networks."""
        return list(self.networks.keys())
    
    async def batch_call(self, network: str, calls: List[Dict]) -> List[Any]:
        """Execute multiple calls in batch for efficiency."""
        if network not in self.networks:
            raise ValueError(f"Network {network} not supported")
        
        w3 = self.networks[network]['web3']
        results = []
        
        for call in calls:
            try:
                # Execute each call based on its type
                if call['type'] == 'get_balance':
                    result = w3.eth.get_balance(call['address'])
                elif call['type'] == 'call_contract':
                    contract = w3.eth.contract(
                        address=call['address'], 
                        abi=call['abi']
                    )
                    result = contract.functions[call['function']](*call['args']).call()
                else:
                    result = None
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error in batch call: {e}")
                results.append(None)
        
        return results
