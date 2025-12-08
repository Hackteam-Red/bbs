# 📋 Hackteam-Red BBS - International Bulletin Board System

![Status](https://img.shields.io/badge/status-active-success)
![Automation](https://img.shields.io/badge/automation-enabled-blue)
![Language](https://img.shields.io/badge/language-english-informational)

Welcome to **Hackteam-Red BBS** - An automated bulletin board system for the red team community. Share jobs, collaborate on projects, find help, and connect with fellow security professionals worldwide! 🌍

## 🎯 What is this?

This is a modern, automated BBS (Bulletin Board System) built on GitHub Discussions with powerful automation features:

- 🤖 **Automated categorization** and labeling
- 📊 **Real-time statistics** and analytics
- 📡 **RSS feed** for staying updated
- 👋 **Welcome bot** for new posts
- 🔔 **Notifications** system
- 📝 **Structured templates** for different post types

## 🚀 Quick Start

### For Users

1. **Browse the Board**: Check [Discussions](../../discussions) to see all posts
2. **Post Something**: Use one of our templates to create a new post
3. **Get Notified**: Watch the repository to get updates
4. **Subscribe to RSS**: Use our [RSS feed](../../blob/main/bbs-feed.xml) in your reader

### Post Categories

| Category | Use For | Label |
|----------|---------|-------|
| 💼 **Jobs & Opportunities** | Job postings, hiring, gigs | `job` |
| 🤝 **Help Wanted** | Need assistance or expertise | `help-wanted` |
| 🔧 **Tools & Resources** | Share scripts, tools, utilities | `tools` |
| 📚 **Learning** | Tutorials, courses, education | `learning` |
| 🎯 **Collaboration** | Project partnerships | `collaboration` |
| 📢 **Announcements** | News, events, updates | `announcement` |

## 📋 How to Post

### Method 1: Using Templates (Recommended)

1. Go to [Discussions](../../discussions)
2. Click **"New discussion"**
3. Choose a template that matches your post type
4. Fill out the form
5. Submit!

The bot will automatically:
- Welcome you with helpful tips
- Add appropriate labels
- Update the bulletin board
- Add your post to RSS feed

### Method 2: Free Form

Just create a new discussion with a descriptive title. The bot will try to categorize it automatically based on keywords.

## 🤖 Automation Features

### Auto-Labeling

The bot automatically adds labels based on keywords in your post:

- **job**: hiring, job, vacancy, position, career
- **help-wanted**: help, need, assistance, support
- **collaboration**: collab, partner, team up, join
- **tools**: tool, script, software, resource
- **learning**: learn, tutorial, course, training
- **urgent**: urgent, asap, immediately, critical
- **red-team**: red team, pentest, offensive
- **blue-team**: blue team, defense, SOC

### Welcome Messages

Every new discussion gets an automated welcome message with:
- Quick tips for getting responses
- Category information
- Community guidelines
- Next steps

### Statistics

Updated every 6 hours:
- Total discussions
- Activity by category
- Top contributors
- Recent activity trends

View current stats: [stats.json](../../blob/main/stats.json)

### RSS Feed

Stay updated without checking GitHub constantly!

**Feed URL**: `https://raw.githubusercontent.com/Hackteam-Red/[REPO]/main/bbs-feed.xml`

Popular RSS readers:
- [Feedly](https://feedly.com)
- [Inoreader](https://www.inoreader.com)
- [NewsBlur](https://newsblur.com)

## 🛠️ Setup Instructions (For Admins)

### Prerequisites

- GitHub repository with Discussions enabled
- GitHub Actions enabled
- Python 3.11+

### Installation

1. **Enable GitHub Discussions**
   ```
   Repository → Settings → Features → ✅ Discussions
   ```

2. **Create Discussion Categories**
   
   Go to Discussions and create these categories:
   - 💼 Jobs & Opportunities
   - 🤝 Help Wanted
   - 🔧 Tools & Resources
   - 📚 Learning
   - 🎯 Collaboration
   - 📢 Announcements
   - 💬 General

3. **Add Repository Structure**
   ```bash
   mkdir -p .github/workflows
   mkdir -p .github/DISCUSSION_TEMPLATE
   ```

4. **Add Files**
   
   Copy these files to your repository:
   - `.github/workflows/bbs-automation.yml` - Main automation workflow
   - `bbs-bot.py` - Python bot script
   - `.github/DISCUSSION_TEMPLATE/*.yml` - Discussion templates
   - `requirements.txt` - Python dependencies

5. **Create requirements.txt**
   ```
   requests>=2.31.0
   PyGithub>=2.1.1
   feedgen>=1.0.0
   ```

6. **Configure Secrets** (if needed)
   
   For advanced features, add these secrets in Settings → Secrets:
   - `DISCORD_WEBHOOK` - For Discord notifications
   - `TELEGRAM_BOT_TOKEN` - For Telegram notifications

7. **Enable GitHub Actions**
   ```
   Repository → Settings → Actions → General
   ✅ Allow all actions and reusable workflows
   
   Workflow permissions:
   ✅ Read and write permissions
   ✅ Allow GitHub Actions to create and approve pull requests
   ```

8. **Test the Setup**
   ```bash
   # Manually trigger the workflow
   Actions → BBS Automation → Run workflow
   ```

### Configuration

Edit `bbs-bot.py` to customize:

```python
# Update organization and repo
ORG = "Hackteam-Red"
REPO = "your-bbs-repo-name"

# Customize welcome message
def send_welcome_message(self, discussion_id: str, author: str):
    message = """
    Your custom welcome message here
    """
```

### Customization

**Auto-labeling rules**: Edit the `keywords` dictionary in `bbs-bot.py`:

```python
keywords = {
    "your-label": ["keyword1", "keyword2", "keyword3"],
}
```

**Workflow schedule**: Edit `.github/workflows/bbs-automation.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Change frequency here
```

## 📊 Analytics & Monitoring

### View Statistics

Check `stats.json` for:
- Total discussions count
- Posts by category
- Top contributors
- Weekly activity

### Monitor Bot Activity

- Check Actions tab for workflow runs
- Review bot comments on discussions
- Check commit history for auto-updates

## 🔧 Advanced Features

### Discord Integration

Add Discord notifications:

```python
# In bbs-bot.py
def send_discord_notification(webhook_url: str, discussion: Dict):
    payload = {
        "embeds": [{
            "title": discussion["title"],
            "description": discussion["body"][:200],
            "color": 3447003,
            "author": {
                "name": discussion["author"]["login"]
            }
        }]
    }
    requests.post(webhook_url, json=payload)
```

### Telegram Integration

Add Telegram bot notifications:

```python
def send_telegram_notification(bot_token: str, chat_id: str, discussion: Dict):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    message = f"🆕 New post: {discussion['title']}\nBy: @{discussion['author']['login']}"
    requests.post(url, json={"chat_id": chat_id, "text": message})
```

### GitHub Pages Dashboard

Create a web dashboard showing BBS statistics and recent posts.

## 🤝 Contributing

Want to improve the BBS? Here's how:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 Community Guidelines

1. **Be Respectful**: Treat everyone with respect
2. **Stay On Topic**: Keep posts relevant to security/red teaming
3. **No Spam**: Don't post duplicate or promotional content
4. **Legal Only**: Only discuss legal security research
5. **Give Back**: Help others when you can

## 🔒 Security & Privacy

- Don't share credentials or sensitive data
- Don't post active exploits for vulnerabilities
- Follow responsible disclosure practices
- Respect NDAs and confidentiality agreements

## 📞 Support

- **Issues**: Report bugs in [Issues](../../issues)
- **Questions**: Ask in [Discussions](../../discussions)
- **Contact**: [GitHub Organization](https://github.com/Hackteam-Red)

## 📄 License

This BBS system is open source. Feel free to fork and customize for your community!

## 🙏 Credits

Built with ❤️ by the Hackteam-Red community

Powered by:
- GitHub Discussions
- GitHub Actions
- Python

---

## 🎉 Ready to Start?

1. [Browse existing posts](../../discussions)
2. [Create your first post](../../discussions/new)
3. [Star this repo](../../stargazers) to stay updated
4. [Follow us](https://github.com/Hackteam-Red) for more projects

**Let's build a strong red team community together! 🚀**

---

*Last updated: 2025-12-08*
