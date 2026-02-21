---
id: 0018
title: minimal-black-white-auth-redesign
stage: misc
date: 2026-02-21
surface: agent
model: claude-haiku-4-5-20251001
feature: 003-ai-chatbot-mcp
branch: main
user: Syed Sufyan
command: /sp.implement
labels: ["ui", "design", "auth", "minimal", "black-white", "poppins", "nature"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/app/(auth)/login/page.tsx
  - frontend/src/app/(auth)/signup/page.tsx
tests:
  - No tests required (visual UI update)
---

## Prompt

i want sing-in and sing-up ui with different theme now only two colors pitch black and white also... on the left side of these oages there is a text and pic.. i just want text... in poppins fonts.. make it more minimal and cozy comfy... use nature pic if u think that will look good.

## Response snapshot

Redesigned both authentication pages with a minimal black and white aesthetic using Poppins font throughout.

**Design Philosophy:**
- Pure black (#000000) and white (#FFFFFF) color scheme
- Poppins font family for all text elements
- Minimal, clean interface with no rounded corners (sharp edges)
- Subtle nature photography as background texture on black panels
- Text-only left panel with large, impactful typography
- Underline-style input fields (bottom border only)

**Login Page Changes:**
1. **Left Panel:**
   - Solid black background with subtle nature image (forest scene) at 10% opacity
   - Large heading: "Welcome Back" in 6xl Poppins semibold
   - Descriptive text: "Step into your space of clarity and focus. Your tasks await."
   - Removed all SVG illustrations
   - Text aligned left for better readability

2. **Right Panel (Form):**
   - Pure white background
   - "Sign In" heading in 4xl Poppins semibold
   - Minimalist input fields with bottom border only (no rounded corners)
   - Black labels and text throughout
   - Black button with no rounded corners
   - Subtle hover effects (scale 1.01)
   - Error messages in black/70 opacity
   - Underlined links with offset

**Signup Page Changes:**
1. **Left Panel:**
   - Solid black background with different nature image (mountain/lake scene) at 10% opacity
   - Large heading: "Begin Your Journey" in 6xl Poppins semibold
   - Descriptive text: "Create your space for productivity and peace. Every great achievement starts here."
   - Text-only design, no illustrations

2. **Right Panel (Form):**
   - Same minimal white design as login
   - "Create Account" heading
   - Three fields: Full Name, Email, Password
   - Consistent styling with login page
   - All form elements use Poppins font

**Typography:**
- Headings: Poppins semibold (font-semibold)
- Body text: Poppins light (font-light)
- Labels: Poppins medium (font-medium)
- All text uses font-poppins class

**Nature Images Used:**
- Login: Forest scene from Unsplash (subtle, calming)
- Signup: Mountain/lake scene from Unsplash (inspiring, peaceful)
- Both at 10% opacity to maintain readability

**Removed Elements:**
- All gradient backgrounds
- All rounded corners (border-radius)
- All colored accents (red, purple, indigo)
- All SVG illustrations and decorative elements
- All shadows except focus rings

The design creates a calm, focused, and professional atmosphere perfect for productivity applications.

## Outcome

- ✅ Impact: Complete minimal redesign with black/white theme and Poppins typography
- 🧪 Tests: No automated tests required - visual design update
- 📁 Files: 2 files modified (login and signup pages)
- 🔁 Next prompts: Could extend minimal theme to dashboard and other pages for consistency
- 🧠 Reflection: Successfully created a cozy, minimal aesthetic using only two colors. The nature backgrounds add subtle warmth without compromising the clean design. Poppins font provides excellent readability and modern feel.

## Evaluation notes (flywheel)

- Failure modes observed: None - clean implementation
- Graders run and results (PASS/FAIL): Visual inspection required
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding subtle animations or micro-interactions to enhance the minimal design without cluttering it
