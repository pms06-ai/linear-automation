import os
import json
from datetime import datetime
from google.cloud import secretmanager
import requests

def create_daily_journal(request):
    """
    Cloud Function to create a daily trading journal issue in Linear
    """
    # Get Linear API key from environment
    api_key = os.environ.get('LINEAR_API_KEY')
    
    if not api_key:
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
    
    response = requests.post(url, json={"query": team_query}, headers=headers)
    teams = response.json().get('data', {}).get('teams', {}).get('nodes', [])
    
    if not teams:
        return {"error": "No teams found"}, 404
    
    team_id = teams[0]['id']
    
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
    
    response = requests.post(
        url,
        json={"query": mutation, "variables": variables},
        headers=headers
    )
    
    result = response.json()
    
    if result.get('data', {}).get('issueCreate', {}).get('success'):
        issue = result['data']['issueCreate']['issue']
        return {
            "success": True,
            "issue": {
                "id": issue['id'],
                "identifier": issue['identifier'],
                "title": issue['title']
            }
        }, 200
    else:
        return {"error": "Failed to create issue", "details": result}, 500
