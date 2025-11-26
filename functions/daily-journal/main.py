import os
import logging
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_daily_journal(request):
    """
    Cloud Function to create a daily trading journal issue in Linear
    """
    logger.info("Starting daily journal creation")
    
    # Get Linear API key from environment
    api_key = os.environ.get('LINEAR_API_KEY')
    
    if not api_key:
        logger.error("LINEAR_API_KEY not configured")
        return {"error": "LINEAR_API_KEY not configured"}, 500
    
    # GraphQL endpoint
    url = "https://api.linear.app/graphql"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    # Get team ID
    team_query = '''
    query {
        teams {
            nodes {
                id
                name
            }
        }
    }
    '''
    
    try:
        response = requests.post(url, json={"query": team_query}, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch teams: {e}")
        return {"error": f"Failed to fetch teams: {str(e)}"}, 500
    
    teams = response.json().get('data', {}).get('teams', {}).get('nodes', [])
    
    if not teams:
        logger.error("No teams found")
        return {"error": "No teams found"}, 404
    
    team_id = teams[0]['id']
    logger.info(f"Using team: {teams[0]['name']} ({team_id})")
    
    # Create issue
    today = datetime.now().strftime('%Y-%m-%d')
    title = f"Trading Journal - {today}"
    
    mutation = '''
    mutation CreateIssue($teamId: String!, $title: String!) {
        issueCreate(input: {
            teamId: $teamId
            title: $title
            labelIds: []
        }) {
            success
            issue {
                id
                identifier
                title
            }
        }
    }
    '''
    
    variables = {
        "teamId": team_id,
        "title": title
    }
    
    try:
        response = requests.post(
            url,
            json={"query": mutation, "variables": variables},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create issue: {e}")
        return {"error": f"Failed to create issue: {str(e)}"}, 500
    
    result = response.json()
    
    if result.get('data', {}).get('issueCreate', {}).get('success'):
        issue = result['data']['issueCreate']['issue']
        logger.info(f"Created issue: {issue['identifier']} - {issue['title']}")
        return {
            "success": True,
            "issue": {
                "id": issue['id'],
                "identifier": issue['identifier'],
                "title": issue['title']
            }
        }, 200
    else:
        logger.error(f"Failed to create issue: {result}")
        return {"error": "Failed to create issue", "details": result}, 500
