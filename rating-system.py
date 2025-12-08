#!/usr/bin/env python3
"""
Rating System for Hackteam-Red BBS
Calculates user rankings based on activity and contributions
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

class RatingSystem:
    def __init__(self, token: str, org: str, repo: str):
        self.token = token
        self.org = org
        self.repo = repo
        self.graphql_url = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Points configuration
        self.points = {
            "discussion_created": 10,
            "comment_posted": 3,
            "discussion_answered": 15,
            "helpful_comment": 5,  # Based on reactions
            "discussion_upvoted": 1,  # Based on reactions
        }
    
    def fetch_all_discussions(self) -> List[Dict]:
        """Fetch all discussions with comments and reactions"""
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
                createdAt
                author {
                  login
                }
                category {
                  name
                }
                answer {
                  id
                  author {
                    login
                  }
                }
                reactions {
                  totalCount
                }
                comments(first: 100) {
                  nodes {
                    id
                    author {
                      login
                    }
                    createdAt
                    reactions {
                      totalCount
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        all_discussions = []
        cursor = None
        has_next = True
        
        while has_next:
            variables = {"org": self.org, "repo": self.repo, "cursor": cursor}
            response = requests.post(
                self.graphql_url,
                headers=self.headers,
                json={"query": query, "variables": variables},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            discussions = data["data"]["repository"]["discussions"]
            all_discussions.extend(discussions["nodes"])
            
            has_next = discussions["pageInfo"]["hasNextPage"]
            cursor = discussions["pageInfo"]["endCursor"]
        
        return all_discussions
    
    def calculate_user_scores(self, discussions: List[Dict]) -> Dict[str, Dict]:
        """Calculate scores for all users"""
        user_stats = defaultdict(lambda: {
            "score": 0,
            "discussions": 0,
            "comments": 0,
            "answers": 0,
            "reactions_received": 0,
            "helpful_comments": 0,
            "recent_activity": 0,
            "categories": defaultdict(int),
            "first_seen": None,
            "last_seen": None
        })
        
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        
        for disc in discussions:
            # Discussion author
            author = disc.get("author", {})
            if author and author.get("login"):
                author_login = author["login"]
                
                # Points for creating discussion
                user_stats[author_login]["score"] += self.points["discussion_created"]
                user_stats[author_login]["discussions"] += 1
                
                # Category tracking
                category = disc.get("category", {}).get("name", "General")
                user_stats[author_login]["categories"][category] += 1
                
                # Reactions on discussion
                reactions = disc.get("reactions", {}).get("totalCount", 0)
                user_stats[author_login]["reactions_received"] += reactions
                user_stats[author_login]["score"] += reactions * self.points["discussion_upvoted"]
                
                # Track dates
                created_at = datetime.fromisoformat(disc["createdAt"].replace("Z", "+00:00"))
                if not user_stats[author_login]["first_seen"] or created_at < user_stats[author_login]["first_seen"]:
                    user_stats[author_login]["first_seen"] = created_at
                if not user_stats[author_login]["last_seen"] or created_at > user_stats[author_login]["last_seen"]:
                    user_stats[author_login]["last_seen"] = created_at
                
                # Recent activity
                if created_at > week_ago:
                    user_stats[author_login]["recent_activity"] += 1
            
            # Answer author (bonus points)
            answer = disc.get("answer")
            if answer and answer.get("author"):
                answer_author = answer["author"].get("login")
                if answer_author:
                    user_stats[answer_author]["score"] += self.points["discussion_answered"]
                    user_stats[answer_author]["answers"] += 1
            
            # Comments
            comments = disc.get("comments", {}).get("nodes", [])
            for comment in comments:
                comment_author = comment.get("author", {})
                if comment_author and comment_author.get("login"):
                    comment_login = comment_author["login"]
                    
                    # Points for commenting
                    user_stats[comment_login]["score"] += self.points["comment_posted"]
                    user_stats[comment_login]["comments"] += 1
                    
                    # Reactions on comment
                    comment_reactions = comment.get("reactions", {}).get("totalCount", 0)
                    if comment_reactions > 0:
                        user_stats[comment_login]["reactions_received"] += comment_reactions
                        user_stats[comment_login]["score"] += comment_reactions * self.points["helpful_comment"]
                        user_stats[comment_login]["helpful_comments"] += 1
                    
                    # Track dates
                    comment_date = datetime.fromisoformat(comment["createdAt"].replace("Z", "+00:00"))
                    if not user_stats[comment_login]["first_seen"] or comment_date < user_stats[comment_login]["first_seen"]:
                        user_stats[comment_login]["first_seen"] = comment_date
                    if not user_stats[comment_login]["last_seen"] or comment_date > user_stats[comment_login]["last_seen"]:
                        user_stats[comment_login]["last_seen"] = comment_date
                    
                    # Recent activity
                    if comment_date > week_ago:
                        user_stats[comment_login]["recent_activity"] += 1
        
        return dict(user_stats)
    
    def assign_ranks(self, user_stats: Dict[str, Dict]) -> List[Dict]:
        """Assign ranks and badges to users"""
        # Sort by score
        sorted_users = sorted(
            user_stats.items(),
            key=lambda x: (x[1]["score"], x[1]["discussions"], x[1]["comments"]),
            reverse=True
        )
        
        rankings = []
        
        for rank, (username, stats) in enumerate(sorted_users, 1):
            # Determine badge/tier
            score = stats["score"]
            if score >= 1000:
                tier = "🏆 Legend"
                tier_level = 6
            elif score >= 500:
                tier = "💎 Diamond"
                tier_level = 5
            elif score >= 250:
                tier = "🥇 Gold"
                tier_level = 4
            elif score >= 100:
                tier = "🥈 Silver"
                tier_level = 3
            elif score >= 50:
                tier = "🥉 Bronze"
                tier_level = 2
            else:
                tier = "🌱 Newcomer"
                tier_level = 1
            
            # Special badges
            badges = []
            if stats["answers"] >= 10:
                badges.append("🎯 Problem Solver")
            if stats["helpful_comments"] >= 20:
                badges.append("⭐ Helpful")
            if stats["discussions"] >= 50:
                badges.append("📢 Active Poster")
            if stats["comments"] >= 100:
                badges.append("💬 Conversationalist")
            if stats["recent_activity"] >= 5:
                badges.append("🔥 Hot Streak")
            
            # Convert categories to regular dict
            categories = dict(stats["categories"])
            
            rankings.append({
                "rank": rank,
                "username": username,
                "score": score,
                "tier": tier,
                "tier_level": tier_level,
                "badges": badges,
                "stats": {
                    "discussions": stats["discussions"],
                    "comments": stats["comments"],
                    "answers": stats["answers"],
                    "reactions_received": stats["reactions_received"],
                    "helpful_comments": stats["helpful_comments"],
                    "recent_activity": stats["recent_activity"],
                    "categories": categories,
                    "first_seen": stats["first_seen"].isoformat() if stats["first_seen"] else None,
                    "last_seen": stats["last_seen"].isoformat() if stats["last_seen"] else None
                }
            })
        
        return rankings
    
    def generate_leaderboard(self, rankings: List[Dict], top_n: int = 50) -> Dict:
        """Generate leaderboard data"""
        leaderboard = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_users": len(rankings),
            "top_users": rankings[:top_n],
            "tier_distribution": defaultdict(int),
            "points_config": self.points
        }
        
        for user in rankings:
            leaderboard["tier_distribution"][user["tier"]] += 1
        
        leaderboard["tier_distribution"] = dict(leaderboard["tier_distribution"])
        
        return leaderboard
    
    def generate_markdown_leaderboard(self, rankings: List[Dict], top_n: int = 50) -> str:
        """Generate markdown leaderboard"""
        md = f"# 🏆 Hackteam-Red BBS Leaderboard\n\n"
        md += f"*Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"
        md += f"**Total Contributors:** {len(rankings)}\n\n"
        md += "---\n\n"
        
        md += "## 🥇 Top Contributors\n\n"
        md += "| Rank | User | Tier | Score | Discussions | Comments | Answers | Badges |\n"
        md += "|------|------|------|-------|-------------|----------|---------|--------|\n"
        
        for user in rankings[:top_n]:
            badges = " ".join(user["badges"][:3]) if user["badges"] else "-"
            md += f"| {user['rank']} | **@{user['username']}** | {user['tier']} | {user['score']} | "
            md += f"{user['stats']['discussions']} | {user['stats']['comments']} | "
            md += f"{user['stats']['answers']} | {badges} |\n"
        
        md += "\n---\n\n"
        
        # Tier distribution
        md += "## 📊 Tier Distribution\n\n"
        tier_dist = defaultdict(int)
        for user in rankings:
            tier_dist[user["tier"]] += 1
        
        for tier in ["🏆 Legend", "💎 Diamond", "🥇 Gold", "🥈 Silver", "🥉 Bronze", "🌱 Newcomer"]:
            count = tier_dist.get(tier, 0)
            md += f"- **{tier}**: {count} users\n"
        
        md += "\n---\n\n"
        
        # Badge explanations
        md += "## 🎖️ Badge System\n\n"
        md += "- 🎯 **Problem Solver**: Provided 10+ accepted answers\n"
        md += "- ⭐ **Helpful**: Received 20+ reactions on comments\n"
        md += "- 📢 **Active Poster**: Created 50+ discussions\n"
        md += "- 💬 **Conversationalist**: Posted 100+ comments\n"
        md += "- 🔥 **Hot Streak**: 5+ activities this week\n"
        
        md += "\n---\n\n"
        
        # Points system
        md += "## 📈 Points System\n\n"
        md += f"- Create discussion: **{self.points['discussion_created']} points**\n"
        md += f"- Post comment: **{self.points['comment_posted']} points**\n"
        md += f"- Answer accepted: **{self.points['discussion_answered']} points**\n"
        md += f"- Helpful comment (per reaction): **{self.points['helpful_comment']} points**\n"
        md += f"- Discussion upvoted (per reaction): **{self.points['discussion_upvoted']} point**\n"
        
        return md


def main():
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    ORG = "Hackteam-Red"
    REPO = os.getenv("REPO_NAME", "bbs")
    
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN not set")
        return
    
    print("🏆 Calculating user rankings...")
    
    rating_system = RatingSystem(GITHUB_TOKEN, ORG, REPO)
    
    # Fetch discussions
    print("📥 Fetching discussions...")
    discussions = rating_system.fetch_all_discussions()
    print(f"✅ Found {len(discussions)} discussions")
    
    # Calculate scores
    print("🔢 Calculating scores...")
    user_stats = rating_system.calculate_user_scores(discussions)
    print(f"✅ Analyzed {len(user_stats)} users")
    
    # Assign ranks
    print("🏅 Assigning ranks...")
    rankings = rating_system.assign_ranks(user_stats)
    
    # Generate leaderboard
    leaderboard = rating_system.generate_leaderboard(rankings)
    
    # Save JSON
    with open("leaderboard.json", "w") as f:
        json.dump(leaderboard, f, indent=2)
    print("✅ Saved leaderboard.json")
    
    # Generate markdown
    md = rating_system.generate_markdown_leaderboard(rankings)
    with open("LEADERBOARD.md", "w") as f:
        f.write(md)
    print("✅ Saved LEADERBOARD.md")
    
    # Show top 10
    print("\n🏆 Top 10 Contributors:")
    for user in rankings[:10]:
        print(f"{user['rank']}. @{user['username']} - {user['tier']} ({user['score']} points)")
    
    print("\n🎉 Rating system completed!")


if __name__ == "__main__":
    main()
