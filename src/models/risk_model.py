"""
Risk Assessment Model

This module combines volatility forecasting and sentiment analysis
to provide comprehensive risk scores for protocol upgrades.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np

from .volatility_model import get_protocol_volatility
from .sentiment_model import get_sentiment_for_protocol, categorize_sentiment

logger = logging.getLogger(__name__)

class RiskAssessment:
    """Risk assessment for protocol upgrades."""
    
    def __init__(self):
        self.weights = {
            'volatility': 0.4,
            'sentiment': 0.3,
            'governance': 0.2,
            'technical': 0.1
        }
    
    async def calculate_risk_score(self, protocol_name: str, proposal_data: Dict = None) -> Dict:
        """
        Calculate comprehensive risk score for a protocol upgrade.
        
        Args:
            protocol_name: Name of the protocol
            proposal_data: Optional proposal metadata
            
        Returns:
            Dictionary containing risk assessment results
        """
        try:
            # Get volatility data
            volatility_data = await get_protocol_volatility(protocol_name)
            volatility_score = self._normalize_volatility_score(volatility_data.get('volatility', 0))
            
            # Get sentiment data
            sentiment_data = get_sentiment_for_protocol(protocol_name)
            sentiment_score = self._normalize_sentiment_score(sentiment_data.get('average_sentiment', 0))
            
            # Calculate governance risk (placeholder - would use real governance data)
            governance_score = self._calculate_governance_risk(proposal_data)
            
            # Calculate technical risk (placeholder - would use contract analysis)
            technical_score = self._calculate_technical_risk(proposal_data)
            
            # Calculate weighted risk score
            risk_score = (
                self.weights['volatility'] * volatility_score +
                self.weights['sentiment'] * sentiment_score +
                self.weights['governance'] * governance_score +
                self.weights['technical'] * technical_score
            )
            
            # Normalize to 0-100 scale
            risk_score = max(0, min(100, risk_score * 100))
            
            return {
                'protocol': protocol_name,
                'overall_risk_score': round(risk_score, 2),
                'risk_category': self._categorize_risk(risk_score),
                'risk_color': self._get_risk_color(risk_score),
                'components': {
                    'volatility': {
                        'score': volatility_score,
                        'raw_value': volatility_data.get('volatility', 0),
                        'weight': self.weights['volatility']
                    },
                    'sentiment': {
                        'score': sentiment_score,
                        'raw_value': sentiment_data.get('average_sentiment', 0),
                        'weight': self.weights['sentiment']
                    },
                    'governance': {
                        'score': governance_score,
                        'weight': self.weights['governance']
                    },
                    'technical': {
                        'score': technical_score,
                        'weight': self.weights['technical']
                    }
                },
                'recommendations': self._generate_recommendations(risk_score, volatility_data, sentiment_data),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk score for {protocol_name}: {e}")
            return {
                'protocol': protocol_name,
                'overall_risk_score': 50.0,  # Default medium risk
                'risk_category': 'Medium',
                'risk_color': '🟡',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _normalize_volatility_score(self, volatility: float) -> float:
        """Convert volatility percentage to 0-1 risk score."""
        if np.isnan(volatility) or volatility <= 0:
            return 0.5  # Default medium risk
        
        # Higher volatility = higher risk
        # Scale: 0-20% vol = low risk, 20-60% = medium, 60%+ = high
        if volatility <= 20:
            return 0.2
        elif volatility <= 60:
            return 0.5
        else:
            return min(1.0, volatility / 100)
    
    def _normalize_sentiment_score(self, sentiment: float) -> float:
        """Convert sentiment score to 0-1 risk score."""
        # Sentiment ranges from -1 (negative) to +1 (positive)
        # More negative sentiment = higher risk
        # Convert to 0-1 scale where 0 = no risk, 1 = high risk
        return max(0, min(1, (1 - sentiment) / 2))
    
    def _calculate_governance_risk(self, proposal_data: Dict = None) -> float:
        """Calculate governance-related risk score."""
        if not proposal_data:
            return 0.5  # Default medium risk
        
        risk_factors = []
        
        # Proposal complexity (simplified)
        description = proposal_data.get('description', '')
        if len(description) > 1000:
            risk_factors.append(0.3)  # Complex proposals are riskier
        
        # Voting participation (if available)
        total_votes = proposal_data.get('total_votes', 0)
        if total_votes < 1000:
            risk_factors.append(0.4)  # Low participation is risky
        
        # Time since proposal
        created = proposal_data.get('created')
        if created:
            # Very recent proposals might be rushed
            risk_factors.append(0.2)
        
        return np.mean(risk_factors) if risk_factors else 0.5
    
    def _calculate_technical_risk(self, proposal_data: Dict = None) -> float:
        """Calculate technical risk score."""
        if not proposal_data:
            return 0.5  # Default medium risk
        
        # This would typically involve:
        # - Smart contract code analysis
        # - Audit status
        # - Upgrade complexity
        # - Historical upgrade success rate
        
        # For now, return a placeholder based on proposal type
        proposal_type = proposal_data.get('type', 'general')
        
        risk_mapping = {
            'governance': 0.3,
            'parameter_change': 0.4,
            'implementation_upgrade': 0.7,
            'emergency': 0.9,
            'general': 0.5
        }
        
        return risk_mapping.get(proposal_type, 0.5)
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk score into readable categories."""
        if risk_score <= 25:
            return 'Low'
        elif risk_score <= 50:
            return 'Medium'
        elif risk_score <= 75:
            return 'High'
        else:
            return 'Critical'
    
    def _get_risk_color(self, risk_score: float) -> str:
        """Get color emoji for risk visualization."""
        if risk_score <= 25:
            return '🟢'  # Green
        elif risk_score <= 50:
            return '🟡'  # Yellow
        elif risk_score <= 75:
            return '🟠'  # Orange
        else:
            return '🔴'  # Red
    
    def _generate_recommendations(self, risk_score: float, volatility_data: Dict, sentiment_data: Dict) -> List[str]:
        """Generate actionable recommendations based on risk assessment."""
        recommendations = []
        
        # Risk level recommendations
        if risk_score <= 25:
            recommendations.append("✅ Low risk - Consider increasing position size")
        elif risk_score <= 50:
            recommendations.append("⚠️ Medium risk - Maintain current position")
        elif risk_score <= 75:
            recommendations.append("🚨 High risk - Consider reducing exposure")
        else:
            recommendations.append("🔥 Critical risk - Strongly consider exiting position")
        
        # Volatility-specific recommendations
        volatility = volatility_data.get('volatility', 0)
        if volatility > 60:
            recommendations.append("📊 High volatility expected - Use stop losses")
        elif volatility > 40:
            recommendations.append("📈 Moderate volatility - Consider DCA strategy")
        
        # Sentiment-specific recommendations
        sentiment = sentiment_data.get('average_sentiment', 0)
        if sentiment < -0.3:
            recommendations.append("😰 Negative sentiment - Monitor social media closely")
        elif sentiment > 0.3:
            recommendations.append("😊 Positive sentiment - Watch for FOMO trading")
        
        return recommendations
    
    def compare_protocols(self, protocol_risks: List[Dict]) -> Dict:
        """Compare risk scores across multiple protocols."""
        if not protocol_risks:
            return {}
        
        risk_scores = [p['overall_risk_score'] for p in protocol_risks]
        
        return {
            'lowest_risk': min(protocol_risks, key=lambda x: x['overall_risk_score']),
            'highest_risk': max(protocol_risks, key=lambda x: x['overall_risk_score']),
            'average_risk': np.mean(risk_scores),
            'risk_distribution': {
                'low': sum(1 for score in risk_scores if score <= 25),
                'medium': sum(1 for score in risk_scores if 25 < score <= 50),
                'high': sum(1 for score in risk_scores if 50 < score <= 75),
                'critical': sum(1 for score in risk_scores if score > 75)
            }
        }

# Convenience functions
async def get_risk_assessment(protocol_name: str, proposal_data: Dict = None) -> Dict:
    """Get risk assessment for a protocol."""
    risk_assessor = RiskAssessment()
    return await risk_assessor.calculate_risk_score(protocol_name, proposal_data)

async def get_portfolio_risk(protocol_names: List[str]) -> Dict:
    """Get risk assessment for multiple protocols."""
    risk_assessor = RiskAssessment()
    
    tasks = [risk_assessor.calculate_risk_score(protocol) for protocol in protocol_names]
    risk_results = await asyncio.gather(*tasks)
    
    return {
        'individual_risks': risk_results,
        'portfolio_analysis': risk_assessor.compare_protocols(risk_results)
    }

# Test function
async def test_risk_assessment():
    """Test the risk assessment functionality."""
    print("Testing Risk Assessment Model...")
    print("=" * 50)
    
    protocols = ['ethereum', 'uniswap', 'aave']
    
    for protocol in protocols:
        print(f"\n{protocol.upper()} Risk Assessment:")
        risk_data = await get_risk_assessment(protocol)
        
        print(f"  Overall Risk Score: {risk_data['overall_risk_score']}")
        print(f"  Risk Category: {risk_data['risk_category']}")
        print(f"  Risk Color: {risk_data['risk_color']}")
        
        if 'components' in risk_data:
            print("  Component Scores:")
            for component, data in risk_data['components'].items():
                print(f"    {component}: {data['score']:.3f} (weight: {data['weight']})")
        
        if 'recommendations' in risk_data:
            print("  Recommendations:")
            for rec in risk_data['recommendations']:
                print(f"    {rec}")
    
    # Test portfolio risk
    print(f"\nPortfolio Risk Analysis:")
    portfolio_risk = await get_portfolio_risk(protocols)
    portfolio_analysis = portfolio_risk['portfolio_analysis']
    
    print(f"  Average Risk: {portfolio_analysis['average_risk']:.2f}")
    print(f"  Lowest Risk: {portfolio_analysis['lowest_risk']['protocol']} ({portfolio_analysis['lowest_risk']['overall_risk_score']})")
    print(f"  Highest Risk: {portfolio_analysis['highest_risk']['protocol']} ({portfolio_analysis['highest_risk']['overall_risk_score']})")

if __name__ == "__main__":
    asyncio.run(test_risk_assessment())
