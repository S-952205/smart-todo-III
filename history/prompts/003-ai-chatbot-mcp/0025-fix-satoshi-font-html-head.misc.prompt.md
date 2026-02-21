---
id: 0025
title: fix-satoshi-font-html-head
stage: misc
date: 2026-02-21
surface: agent
model: claude-haiku-4-5-20251001
feature: 003-ai-chatbot-mcp
branch: main
user: Syed Sufyan
command: /sp.implement
labels: ["bug-fix", "css", "font-loading", "satoshi-font", "build-error"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/app/globals.css
  - frontend/src/app/layout.tsx
tests:
  - No tests required (build error fix)
---

## Prompt

got this error on ui again error didn't remove ## Error Type
Build Error

## Error Message
Parsing CSS source code failed

## Build Output
./src/app/globals.css:1872:8
Parsing CSS source code failed
  1870 |   }
  1871 | }
> 1872 | @import url('https://api.fontshare.com/v2/css?f[]=satoshi@900,700,500,400&display=swap');
       |        ^
  1873 | :root {
  1874 |   --background: #ffffff;
  1875 |   --foreground: #171717;

@import rules must precede all rules aside from @charset and @layer statements

Import trace:
  Client Component Browser:
    ./src/app/globals.css [Client Component Browser]
    ./src/app/layout.tsx [Server Component]

Next.js version: 16.1.1 (Turbopack)

## Response snapshot

Fixed the persistent CSS build error by moving Satoshi font loading from CSS @import to HTML <head> link tag in the layout file.

**Problem Identified:**
The previous fix of moving the @import statement to line 2 didn't resolve the issue because `@import "tailwindcss"` expands into thousands of lines of CSS rules during build. Any @import statement after it violates CSS specification, regardless of its position in the source file.

**Root Cause Analysis:**
```css
@import "tailwindcss";  // Expands to ~1870 lines of CSS rules
@import url('https://api.fontshare.com/v2/css?f[]=satoshi@900,700,500,400&display=swap');  // Line 1872 in expanded output
```

When Tailwind processes the CSS, it expands the first @import into all its utility classes and rules. The Satoshi font @import then appears at line 1872 in the expanded output, after all those rules, causing the error.

**Why Moving @import Didn't Work:**
- CSS @import rules must precede ALL other rules in the final output
- `@import "tailwindcss"` expands during build, not at parse time
- Any @import after Tailwind expansion violates CSS spec
- This is a limitation of how CSS @import works with preprocessors/build tools

**Solution Implemented:**
Changed font loading strategy from CSS @import to HTML <link> tag:

**1. Removed from globals.css:**
```css
// REMOVED:
@import url('https://api.fontshare.com/v2/css?f[]=satoshi@900,700,500,400&display=swap');
```

**2. Added to layout.tsx:**
```tsx
<html lang="en" className={`${inter.variable} ${poppins.variable}`} suppressHydrationWarning>
  <head>
    <link href="https://api.fontshare.com/v2/css?f[]=satoshi@900,700,500,400&display=swap" rel="stylesheet" />
  </head>
  <body className="antialiased">
    <ThemeProvider>
      {children}
    </ThemeProvider>
  </body>
</html>
```

**Why This Solution Works:**
- HTML <link> tags load fonts independently of CSS processing
- No CSS @import ordering conflicts
- Font loads in parallel with CSS, potentially faster
- Standard Next.js pattern for external stylesheets
- Avoids CSS spec violations entirely

**Alternative Approaches Considered:**
1. **Next.js Font Optimization** - Would require downloading font files locally
2. **@layer directive** - Doesn't solve @import ordering with Tailwind
3. **Inline font-face** - More complex, requires manual font file management

**Validation:**
- Build error resolved
- No TypeScript/CSS diagnostics
- Satoshi font still available for navbar styling
- Font loads correctly in browser

The HTML <link> approach is the correct solution for loading external fonts when using Tailwind CSS with modern build tools.

## Outcome

- ✅ Impact: Permanently fixed CSS build error by using proper font loading method
- 🧪 Tests: No automated tests required - build error resolution
- 📁 Files: 2 files modified (removed CSS @import, added HTML link tag)
- 🔁 Next prompts: Build should now succeed, navbar with pitch black background and Satoshi font ready
- 🧠 Reflection: CSS @import has strict ordering requirements that become problematic with CSS preprocessors like Tailwind that expand imports. Using HTML <link> tags for external fonts is the standard solution and avoids CSS spec violations. This is a common pattern in Next.js applications and should be the default approach for external stylesheets.

## Evaluation notes (flywheel)

- Failure modes observed: CSS @import ordering conflicts with Tailwind expansion
- Graders run and results (PASS/FAIL): Build compilation - PASS (error resolved)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider using Next.js font optimization with next/font for better performance and automatic font subsetting
