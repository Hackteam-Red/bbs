#!/usr/bin/env python3
"""
Hackteam-Red BBS Automation Bot
Automates GitHub Discussions management for team bulletin board
"""

import os
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional

class BBSBot:
    def __init__(self, token: str, org: str, repo: str):
        self.token = token
        self.org = org
        self.repo = repo
        self.api_base = "https://api.github.com"
        self.graphql_url = f"{self.api_base}/graphql"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def graphql_query(self, query: str, variables: Dict = None) -> Dict:
        """Execute GraphQL query"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(
            self.graphql_url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_discussions(self, category: Optional[str] = None) -> List[Dict]:
        """Fetch all discussions from repository"""
        query = """
        query($org: String!, $repo: String!, $cursor: String) {
          repository(owner: $org, name: $repo) {
            discussions(first: 100, after: $cursor) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                id
                title
                body
                createdAt
                updatedAt
                author {
                  login
                }
                category {
                  name
                }
                labels(first: 10) {
                  nodes {
                    name
                  }
                }
                comments(first: 1) {
                  totalCount
                }
              }
            }
          }
        }
        """
        
        variables = {"org": self.org, "repo": self.repo}
        result = self.graphql_query(query, variables)
        
        discussions = result.get("data", {}).get("repository", {}).get("discussions", {}).get("nodes", [])
        
        if category:
            discussions = [d for d in discussions if d.get("category", {}).get("name") == category]
        
        return discussions
    
    def auto_label_discussion(self, discussion_id: str, title: str, body: str):
        """Automatically add labels based on content"""
        labels = []
        
        keywords = {
            "job": ["hiring", "job", "vacancy", "position", "career", "work"],
            "help-wanted": ["help", "need", "looking for", "assistance", "support"],
            "collaboration": ["collab", "partner", "team up", "join", "together"],
            "tools": ["tool", "script", "software", "resource", "utility"],
            "learning": ["learn", "tutorial", "course", "training", "education"],
            "urgent": ["urgent", "asap", "immediately", "critical", "emergency"]
        }
        
        content = f"{title} {body}".lower()
        
        for label, words in keywords.items():
            if any(word in content for word in words):
                labels.append(label)
        
        if labels:
            self.add_labels_to_discussion(discussion_id, labels)
        
        return labels
    
    def add_labels_to_discussion(self, discussion_id: str, labels: List[str]):
        """Add labels to a discussion"""
        # Note: GitHub Discussions labels require GraphQL mutations
        mutation = """
        mutation($discussionId: ID!, $labelIds: [ID!]!) {
          addLabelsToLabelable(input: {labelableId: $discussionId, labelIds: $labelIds}) {
            clientMutationId
          }
        }
        """
        # This requires label IDs which need to be fetched first
        print(f"Would add labels {labels} to discussion {discussion_id}")
    
    def send_welcome_message(self, discussion_id: str, author: str):
        """Send automated welcome message to new discussion"""
        message = f"""
👋 **Welcome to Hackteam-Red BBS, @{author}!**

Thank you for posting! Here are some quick tips:

- 🏷️ **Use labels** to categorize your post
- 📝 **Be specific** in your description
- 🔔 **Enable notifications** to get responses
- ✅ **Mark as answered** when resolved

Our community will respond soon! 🚀

---
*This is an automated message from BBS Bot*
"""
        self.add_comment_to_discussion(discussion_id, message)
    
    def add_comment_to_discussion(self, discussion_id: str, body: str):
        """Add a comment to discussion"""
        mutation = """
        mutation($discussionId: ID!, $body: String!) {
          addDiscussionComment(input: {discussionId: $discussionId, body: $body}) {
            comment {
              id
            }
          }
        }
        """
        variables = {"discussionId": discussion_id, "body": body}
        return self.graphql_query(mutation, variables)
    
    def generate_rss_feed(self, discussions: List[Dict]) -> str:
        """Generate RSS feed from discussions"""
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom
        
        rss = Element('rss', version='2.0')
        channel = SubElement(rss, 'channel')
        
        SubElement(channel, 'title').text = 'Hackteam-Red BBS'
        SubElement(channel, 'link').text = f'https://github.com/{self.org}/{self.repo}/discussions'
        SubElement(channel, 'description').text = 'Red Team Community Bulletin Board'
        SubElement(channel, 'language').text = 'en'
        
        for disc in discussions[:20]:  # Latest 20
            item = SubElement(channel, 'item')
            SubElement(item, 'title').text = disc.get('title', 'No title')
            SubElement(item, 'description').text = disc.get('body', '')[:500]
            SubElement(item, 'author').text = disc.get('author', {}).get('login', 'Unknown')
            SubElement(item, 'pubDate').text = disc.get('createdAt', '')
            
        xml_str = minidom.parseString(tostring(rss)).toprettyxml(indent="  ")
        return xml_str
    
    def get_statistics(self) -> Dict:
        """Generate BBS statistics"""
        discussions = self.get_discussions()
        
        stats = {
            "total_discussions": len(discussions),
            "categories": {},
            "top_contributors": {},
            "recent_activity": 0,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        for disc in discussions:
            # Category stats
            category = disc.get("category", {}).get("name", "Uncategorized")
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            
            # Contributor stats
            author = disc.get("author", {}).get("login", "Unknown")
            stats["top_contributors"][author] = stats["top_contributors"].get(author, 0) + 1
            
            # Recent activity (last 7 days)
            created = datetime.fromisoformat(disc.get("createdAt", "").replace("Z", "+00:00"))
            if (datetime.now(created.tzinfo) - created).days <= 7:
                stats["recent_activity"] += 1
        
        # Sort top contributors
        stats["top_contributors"] = dict(
            sorted(stats["top_contributors"].items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return stats
    
    def generate_markdown_board(self, discussions: List[Dict]) -> str:
        """Generate markdown bulletin board view"""
        md = "# 📋 Hackteam-Red BBS - Bulletin Board\n\n"
        md += f"*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"
        md += "---\n\n"
        
        # Group by category
        categories = {}
        for disc in discussions:
            cat = disc.get("category", {}).get("name", "Uncategorized")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(disc)
        
        # Generate sections
        for category, items in sorted(categories.items()):
            md += f"## 🔖 {category}\n\n"
            
            for disc in items[:10]:  # Latest 10 per category
                title = disc.get("title", "No title")
                author = disc.get("author", {}).get("login", "Unknown")
                comments = disc.get("comments", {}).get("totalCount", 0)
                created = disc.get("createdAt", "")[:10]
                
                md += f"- **[{title}]** by @{author} • {created} • 💬 {comments}\n"
            
            md += "\n"
        
        return md


def main():
    # Configuration from environment variables
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    ORG = "Hackteam-Red"
    REPO = os.getenv("REPO_NAME", "bbs")  # Your BBS repository name
    
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        return
    
    bot = BBSBot(GITHUB_TOKEN, ORG, REPO)
    
    print("🤖 Starting BBS Bot...")
    
    # Fetch discussions
    print("📥 Fetching discussions...")
    discussions = bot.get_discussions()
    print(f"✅ Found {len(discussions)} discussions")
    
    # Generate statistics
    print("📊 Generating statistics...")
    stats = bot.get_statistics()
    print(json.dumps(stats, indent=2))
    
    # Generate RSS feed
    print("📡 Generating RSS feed...")
    rss = bot.generate_rss_feed(discussions)
    with open("bbs-feed.xml", "w") as f:
        f.write(rss)
    print("✅ RSS feed saved to bbs-feed.xml")
    
    # Generate markdown board
    print("📝 Generating markdown board...")
    board = bot.generate_markdown_board(discussions)
    with open("BOARD.md", "w") as f:
        f.write(board)
    print("✅ Board saved to BOARD.md")
    
    print("\n🎉 BBS Bot completed successfully!")


if __name__ == "__main__":
    main()
