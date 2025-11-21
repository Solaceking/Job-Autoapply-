# 🤖 GenSpark Chat Handover Prompt

## How to Use This Prompt

When transitioning this project to a new GenSpark chat session, copy the prompt below and paste it as your **first message** to the new chat. This ensures complete context transfer and seamless continuity.

---

## 📋 Copy This Prompt (Start Below This Line)

---

Hello! I'm taking over the **LinkedIn Auto Job Applier** project from a previous GenSpark chat session. I need to understand the complete project context for seamless continuity.

**Repository:** https://github.com/Solaceking/Job-Autoapply-  
**Current Branch:** `genspark_ai_developer`  
**Working Directory:** `/home/user/webapp`

## 🎯 Critical Instructions for You:

### 1. **Read Project Handover Documentation**
Please immediately read this file in its entirety:
```
/home/user/webapp/GENSPARK_HANDOVER.md
```

This document contains:
- Complete project overview
- All recent critical fixes with commit hashes
- Git workflow requirements (MANDATORY)
- Architecture and design system
- File structure and purposes
- Testing protocols
- Known issues and solutions

### 2. **Verify Current State**
After reading the handover doc, please:

```bash
# Check working directory
cd /home/user/webapp && pwd

# Check git status
cd /home/user/webapp && git status
cd /home/user/webapp && git log --oneline -10

# Check current PR
cd /home/user/webapp && gh pr view genspark_ai_developer --json url,title,number

# List project structure
cd /home/user/webapp && ls -la
cd /home/user/webapp && ls -la Auto_job_applier_linkedIn/
```

### 3. **Test Application**
Verify the application works:

```bash
cd /home/user/webapp && python Auto_job_applier_linkedIn/main.py
```

Expected behavior:
- Material Design 3 GUI launches
- No console errors
- All pages navigable (Dashboard, Job Search, AI Features, Settings, Logs)
- AI provider dropdown works with dynamic model updates

### 4. **Understand Git Workflow (CRITICAL)**

**This project has STRICT git workflow requirements that you MUST follow:**

#### ❌ NEVER:
- Leave code uncommitted
- Skip PR creation/update
- Push without syncing with remote first
- Skip commit squashing before PR
- Forget to share PR link with user

#### ✅ ALWAYS (For EVERY Code Change):
```bash
# Step 1: Make changes

# Step 2: IMMEDIATELY commit
git add .
git commit -m "type(scope): clear description"

# Step 3: SYNC with remote BEFORE pushing
git fetch origin master
git rebase origin/master
# Resolve conflicts if any (prefer remote code)

# Step 4: SQUASH all local commits into ONE
git reset --soft HEAD~N  # N = number of commits
git commit -m "comprehensive message"

# Step 5: Push (force if needed after rebase)
git push origin genspark_ai_developer -f

# Step 6: PR updates automatically, but SHARE the link
gh pr view genspark_ai_developer --json url
```

### 5. **Remember Directory Constraints**

**ALL operations must be in `/home/user/webapp`**

The Bash tool ALWAYS starts at `/home/user`, so EVERY command must begin with:
```bash
cd /home/user/webapp && your_command
```

Examples:
```bash
cd /home/user/webapp && python main.py
cd /home/user/webapp && git status
cd /home/user/webapp && ls -la
```

### 6. **Key Technical Context**

**Python Version:** 3.12+ (distutils was removed - we have a compatibility fix)

**GUI Framework:** PySide6 (Qt6) with Material Design 3
- Main class: `MaterialDesignGUI` (NOT `MainWindow`)
- Located in: `Auto_job_applier_linkedIn/gui.py`

**Recent Critical Fixes (Commits in GENSPARK_HANDOVER.md):**
1. AI config save import error → Relative imports
2. Distutils error → Compatibility shim  
3. Static model selector → Dynamic updates with signals
4. Import error on launch → Correct class name
5. AttributeError → Safety checks in _log()
6. Text visibility → QGroupBox stylesheet fixes

**Material Design System:**
- Colors: `MaterialColors` class (lines 7-33 in gui.py)
- Typography: `MaterialTypography` class (lines 35-52)
- Navigation rail: 88px fixed width
- Card radius: 16px, Button radius: 8px

**AI Providers (9 Total):**
OpenAI, Google Gemini, **Groq (Priority)**, DeepSeek, Anthropic, xAI, Mistral, Cohere, Ollama (Local)

### 7. **Current Project Status**

**Completed:**
- ✅ Material Design 3 complete overhaul
- ✅ AI question answering, job matching, learning DB
- ✅ 9 AI provider support with 2025 models
- ✅ All critical bugs fixed (see handover doc)
- ✅ Text visibility and ComboBox fixes pushed

**Current State:**
- Latest commit: Text visibility fixes (Commit: e7ad449)
- PR: https://github.com/Solaceking/Job-Autoapply-/pull/1
- Status: Awaiting user testing feedback

**Known Issues:**
- None currently - awaiting user testing

### 8. **What User Expects From You**

The user expects you to:
- ✅ Understand the project without asking for repeated context
- ✅ Fix bugs efficiently with proper testing
- ✅ Follow git workflow strictly (commit → sync → squash → push → share PR)
- ✅ Maintain Material Design 3 consistency
- ✅ Update documentation when making significant changes
- ✅ Test before committing
- ✅ Communicate clearly with technical details

### 9. **If User Reports Issues**

**Standard debugging workflow:**

1. Ask for specific details (error messages, screenshots, steps to reproduce)
2. Read relevant file sections using Read tool
3. Check git history: `git log --grep="keyword"`
4. Make targeted fix with inline comments
5. Test if possible
6. Follow git workflow (commit → sync → squash → push → PR)
7. Share PR link with user
8. Ask user to test: `git pull origin genspark_ai_developer && python main.py`

### 10. **Files You Should Read Now**

In priority order:

1. **CRITICAL:** `/home/user/webapp/GENSPARK_HANDOVER.md` (complete context)
2. **High:** `/home/user/webapp/README.md` (user perspective)
3. **High:** `/home/user/webapp/Auto_job_applier_linkedIn/gui.py` (main GUI, ~1400 lines)
4. **Medium:** `/home/user/webapp/MATERIAL_DESIGN_COMPLETE.md` (design details)
5. **Medium:** `/home/user/webapp/DEPLOYMENT.md` (deployment guide)

---

## ✅ Confirmation Checklist

After reading everything, please confirm you understand:

- [ ] Project purpose and technologies
- [ ] Git workflow requirements (commit → sync → squash → push → PR)
- [ ] Directory constraints (`/home/user/webapp` + cd prefix)
- [ ] Recent critical fixes and their commit hashes
- [ ] Material Design 3 architecture
- [ ] AI provider integration
- [ ] Testing protocol
- [ ] Current project status and PR

---

## 🚀 Ready to Start

Once you've completed the above, please respond with:

1. Confirmation you've read `GENSPARK_HANDOVER.md`
2. Summary of current project status
3. Git log of last 5 commits
4. Current PR URL and status
5. Any immediate observations or concerns

Then I can provide you with new tasks or bug reports.

Thank you! Let's maintain the excellent work from the previous session. 🎯

---

## 📋 End of Handover Prompt

---

## Additional Notes for Current User

### When to Use This Prompt

Use this handover prompt when:
1. **Starting a new GenSpark chat** for this project
2. **Context window is getting full** and you need to "reset"
3. **Switching between different AI assistants** working on this project
4. **After a long break** from the project (days/weeks)

### What This Prompt Does

✅ **Directs new chat to read handover doc** - Most important  
✅ **Provides immediate commands** to verify state  
✅ **Emphasizes git workflow** - Critical for this project  
✅ **Sets expectations** for behavior and quality  
✅ **Gives debugging framework** - Standard approach  
✅ **Includes checklist** - Ensures nothing is missed

### Customization Tips

You can modify the prompt to:
- Add specific user preferences (communication style, etc.)
- Highlight current priorities or urgent issues
- Include recent user feedback or pain points
- Add specific areas needing attention

### Maintenance

Update this prompt template when:
- Project structure changes significantly
- New critical files are added
- Git workflow evolves
- New conventions are established

---

**Pro Tip:** Keep this prompt template and `GENSPARK_HANDOVER.md` in sync. When you update one, update the other to reference the changes.
