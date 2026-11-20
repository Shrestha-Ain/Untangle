/**
 * Markdown & Pedagogical Rich Card Renderer for Regulus AI.
 * Converts raw markdown, formulas, code snippets, and structured pedagogical callouts
 * into beautiful, accessible, interactive HTML with zero runtime dependencies.
 * Full support for Light and Dark modes.
 */

/**
 * Cleans raw string received from LLM or backend.
 * Strips Python AST/JSON list wrappers like `[{'type': 'text', 'text': "..."}]`
 * and eliminates meta-commentary apologies.
 */
export function cleanAssistantContent(raw: string): string {
  if (!raw) return ''

  let text = String(raw).trim()

  // 1. Direct prefix extraction for stringified Python list/dict representation:
  // e.g. `[{'type': 'text', 'text': "..."}]` or `[{"type": "text", "text": "..."}]`
  const prefixMatch = text.match(/^\[\s*\{\s*['"]type['"]\s*:\s*['"]text['"]\s*,\s*['"]text['"]\s*:\s*(['"])/)
  if (prefixMatch) {
    const quoteChar = prefixMatch[1]
    text = text.substring(prefixMatch[0].length)
    text = text.replace(new RegExp(`\\${quoteChar}\\s*\\}?\\s*\\]?$`), '')
  } else if (
    (text.startsWith('[') && (text.includes("'type': 'text'") || text.includes('"type": "text"'))) ||
    (text.startsWith('{') && (text.includes("'text':") || text.includes('"text":')))
  ) {
    let extracted: string | null = null

    // Strategy A: JSON parse
    try {
      const parsed = JSON.parse(text)
      if (Array.isArray(parsed)) {
        extracted = parsed.map((p) => (typeof p === 'object' && p ? p.text || '' : String(p))).join('')
      } else if (typeof parsed === 'object' && parsed) {
        extracted = parsed.text || parsed.content || null
      }
    } catch {
      // Not valid JSON
    }

    // Strategy B: Multiline Regex with [\s\S]
    if (!extracted) {
      const match = text.match(/['"]text['"]\s*:\s*(['"])((?:\\.|(?!\1)[\s\S])*)\1/)
      if (match && match[2]) {
        extracted = match[2]
      }
    }

    // Strategy C: Structural prefix/suffix stripping
    if (!extracted) {
      let candidate = text
      candidate = candidate.replace(/^\[\s*\{\s*['"]type['"]\s*:\s*['"]text['"]\s*,\s*['"]text['"]\s*:\s*['"]?/, '')
      candidate = candidate.replace(/['"]?\s*\}\s*\]$/, '')
      if (candidate !== text) {
        extracted = candidate
      }
    }

    if (extracted !== null && extracted.trim().length > 0) {
      text = extracted.trim()
    }
  }

  // 2. Unescape literal escaped backslashes (\n, \", \', \t)
  if (text.includes('\\n')) {
    text = text.replace(/\\n/g, '\n')
  }
  if (text.includes('\\"')) {
    text = text.replace(/\\"/g, '"')
  }
  if (text.includes("\\'")) {
    text = text.replace(/\\'/g, "'")
  }
  if (text.includes('\\t')) {
    text = text.replace(/\\t/g, '  ')
  }

  // 3. Remove apologetic robotic meta-commentary from LLM
  text = text.replace(
    /^(?:(?:As|Since|Although|Because|Note:?)\s+(?:the\s+)?(?:local\s+)?(?:context\s+)?(?:chunks?|text|document|excerpts?|passages?)[^\n]*(?:contain\s+no|do\s+not\s+contain|does\s+not\s+contain|no\s+direct|not\s+found)[^\n]*\n*)+/gi,
    ''
  )
  text = text.replace(
    /^(?:As an AI language model[^\n]*\n*|Based on general knowledge since[^\n]*\n*|Note:\s*Local context chunks?[^\n]*\n*)/gi,
    ''
  )

  // 4. Remove leading horizontal rules or blank lines left after removing preamble
  text = text.replace(/^(?:(?:\s*---|\s*\*\*\*|\s*___)\s*\n*)+/g, '').trim()

  return text
}

/**
 * Escapes HTML characters to prevent XSS.
 */
function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

/**
 * Formats inline Markdown elements (bold, italic, code, formulas).
 */
function formatInline(text: string): string {
  let formatted = escapeHtml(text)

  // Math expressions: $formula$ or $$formula$$
  formatted = formatted.replace(
    /\$\$([^$]+)\$\$/g,
    '<span class="inline-block px-1.5 py-0.5 my-0.5 font-mono text-[11px] font-bold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 rounded border border-emerald-200 dark:border-emerald-800">$1</span>'
  )
  formatted = formatted.replace(
    /\$([^$]+)\$/g,
    '<span class="inline-block px-1 py-0.5 font-mono text-[11px] font-bold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 rounded border border-emerald-200 dark:border-emerald-800">$1</span>'
  )

  // Inline code: `code`
  formatted = formatted.replace(
    /`([^`]+)`/g,
    '<code class="font-mono text-[10.5px] bg-slate-100 dark:bg-slate-800 text-teal-800 dark:text-teal-300 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700 font-bold">$1</code>'
  )

  // Bold: **text**
  formatted = formatted.replace(
    /\*\*([^*]+)\*\*/g,
    '<strong class="font-bold text-slate-900 dark:text-slate-100">$1</strong>'
  )

  // Italic: *text*
  formatted = formatted.replace(
    /\*([^*]+)\*/g,
    '<em class="italic text-slate-700 dark:text-slate-300">$1</em>'
  )

  return formatted
}

/**
 * Parses markdown blocks and returns structured interactive HTML.
 */
export function renderMarkdown(content: string): string {
  if (!content) return ''

  const cleaned = cleanAssistantContent(content)
  const lines = cleaned.split('\n')
  const output: string[] = []

  let inCodeBlock = false
  let codeBuffer: string[] = []
  let codeLang = ''

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i]
    const trimmed = rawLine.trim()

    // 1. Code Blocks
    if (trimmed.startsWith('```')) {
      if (inCodeBlock) {
        // Close code block
        const escapedCode = escapeHtml(codeBuffer.join('\n'))
        output.push(`
          <div class="my-2.5 rounded-xl overflow-hidden border border-[#2D3748] bg-[#1A202C] text-[#E2E8F0] shadow-sm">
            <div class="px-3 py-1 bg-[#2D3748]/70 border-b border-[#4A5568] flex items-center justify-between text-[10px] font-mono text-[#A0AEC0]">
              <span>${codeLang || 'CODE'}</span>
              <span>SYNTAX</span>
            </div>
            <pre class="p-3 text-[11px] font-mono leading-relaxed overflow-x-auto selection:bg-[#4A5568]"><code>${escapedCode}</code></pre>
          </div>
        `)
        codeBuffer = []
        inCodeBlock = false
        codeLang = ''
      } else {
        inCodeBlock = true
        codeLang = trimmed.replace('```', '').trim()
      }
      continue
    }

    if (inCodeBlock) {
      codeBuffer.push(rawLine)
      continue
    }

    // 2. Horizontal Rules
    if (trimmed === '---' || trimmed === '***' || trimmed === '___') {
      output.push('<hr class="my-3 border-t border-slate-200 dark:border-slate-800" />')
      continue
    }

    // 3. Headings
    if (trimmed.startsWith('### ')) {
      const headingText = formatInline(trimmed.replace('### ', ''))
      output.push(`
        <h3 class="text-xs font-bold text-slate-900 dark:text-slate-100 mt-3 mb-1.5 flex items-center gap-1.5 uppercase tracking-wide">
          <span class="w-1.5 h-3 bg-teal-600 dark:bg-teal-400 rounded-full inline-block"></span>
          <span>${headingText}</span>
        </h3>
      `)
      continue
    }

    if (trimmed.startsWith('## ')) {
      const headingText = formatInline(trimmed.replace('## ', ''))
      output.push(`
        <h2 class="text-xs font-extrabold text-slate-900 dark:text-slate-100 mt-3.5 mb-1.5 flex items-center gap-1.5">
          <span>${headingText}</span>
        </h2>
      `)
      continue
    }

    if (trimmed.startsWith('# ')) {
      const headingText = formatInline(trimmed.replace('# ', ''))
      output.push(`
        <h1 class="text-sm font-black text-slate-900 dark:text-slate-100 mt-4 mb-2 pb-1 border-b border-slate-200 dark:border-slate-800">
          ${headingText}
        </h1>
      `)
      continue
    }

    // 4. Pedagogical Callout Cards
    // E.g. 💡 Analogy, ⚙️ Mechanism, ⚠️ Exam Trap, 🗺️ Roadmap, 💬 Interactive Check
    if (
      trimmed.startsWith('💡') ||
      trimmed.startsWith('⚙️') ||
      trimmed.startsWith('⚠️') ||
      trimmed.startsWith('🗺️') ||
      trimmed.startsWith('🎯') ||
      trimmed.startsWith('💬')
    ) {
      let cardStyle = 'bg-slate-50 dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200'
      let badgeStyle = 'bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200'
      let badgeLabel = 'Insight'

      if (trimmed.startsWith('💡')) {
        cardStyle = 'bg-amber-50 dark:bg-amber-950/40 border-2 border-amber-300 dark:border-amber-700 text-amber-950 dark:text-amber-200'
        badgeStyle = 'bg-amber-500 text-white font-black'
        badgeLabel = '💡 Real-World Analogy'
      } else if (trimmed.startsWith('⚙️')) {
        cardStyle = 'bg-emerald-50 dark:bg-emerald-950/40 border-2 border-emerald-400 dark:border-emerald-700 text-emerald-950 dark:text-emerald-200'
        badgeStyle = 'bg-emerald-600 text-white font-black'
        badgeLabel = '⚙️ Technical Mechanism'
      } else if (trimmed.startsWith('⚠️')) {
        cardStyle = 'bg-rose-50 dark:bg-rose-950/40 border-2 border-rose-400 dark:border-rose-700 text-rose-950 dark:text-rose-200'
        badgeStyle = 'bg-rose-500 text-white font-black'
        badgeLabel = '⚠️ High-Yield Exam Trap'
      } else if (trimmed.startsWith('🗺️')) {
        cardStyle = 'bg-blue-50 dark:bg-blue-950/40 border-2 border-blue-400 dark:border-blue-700 text-blue-950 dark:text-blue-200'
        badgeStyle = 'bg-blue-600 text-white font-black'
        badgeLabel = '🗺️ Curriculum Position'
      } else if (trimmed.startsWith('🎯')) {
        cardStyle = 'bg-indigo-50 dark:bg-indigo-950/40 border-2 border-indigo-400 dark:border-indigo-700 text-indigo-950 dark:text-indigo-200'
        badgeStyle = 'bg-indigo-600 text-white font-black'
        badgeLabel = '🎯 Core Takeaway'
      } else if (trimmed.startsWith('💬')) {
        cardStyle = 'bg-purple-50 dark:bg-purple-950/40 border-2 border-purple-400 dark:border-purple-700 text-purple-950 dark:text-purple-200'
        badgeStyle = 'bg-purple-600 text-white font-black'
        badgeLabel = '💬 Interactive Check'
      }

      // Collect contiguous lines belonging to this callout card until an empty line
      const cardLines = [trimmed]
      while (i + 1 < lines.length && lines[i + 1].trim() !== '' && !lines[i + 1].trim().startsWith('```')) {
        i++
        cardLines.push(lines[i].trim())
      }

      const cardBody = cardLines.map((l) => formatInline(l)).join('<br/>')

      output.push(`
        <div class="my-2.5 p-3 rounded-xl border ${cardStyle} shadow-2xs space-y-1 text-xs leading-relaxed">
          <div class="flex items-center gap-1.5 font-bold font-mono text-[10px] tracking-wide mb-1">
            <span class="px-2 py-0.5 rounded-full ${badgeStyle}">${badgeLabel}</span>
          </div>
          <div>${cardBody}</div>
        </div>
      `)
      continue
    }

    // 4.5. Interactive Follow-up Question Chips: `👉 ...`
    if (trimmed.startsWith('👉') || trimmed.startsWith('• 👉') || trimmed.startsWith('* 👉')) {
      const cleanQ = trimmed
        .replace(/^[-*•]?\s*👉\s*/, '')
        .replace(/^[*_"]+|[*_"]+$/g, '')
        .trim()
      output.push(`
        <button
          type="button"
          data-followup-question="${escapeHtml(cleanQ)}"
          class="interactive-followup-chip my-1 mr-1.5 px-3 py-1.5 rounded-xl bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/60 dark:hover:bg-blue-900/80 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300 text-left text-xs font-semibold inline-flex items-center gap-1.5 transition-all duration-150 hover:scale-[1.01] active:scale-[0.98] cursor-pointer group shadow-2xs"
          title="Click to ask this question immediately"
        >
          <span class="text-blue-500 group-hover:translate-x-0.5 transition-transform text-xs">💬</span>
          <span class="flex-1">${escapeHtml(cleanQ)}</span>
          <span class="material-symbols-outlined text-[13px] opacity-60 group-hover:opacity-100 transition-opacity">arrow_forward</span>
        </button>
      `)
      continue
    }

    // 5. Bullet Lists: `• `, `- `, `* `
    if (/^[-*•]\s+/.test(trimmed)) {
      const itemText = formatInline(trimmed.replace(/^[-*•]\s+/, ''))
      output.push(`
        <div class="flex items-start gap-2 ml-1 my-1 text-xs leading-relaxed text-slate-800 dark:text-slate-200">
          <span class="text-teal-600 dark:text-teal-400 mt-1 text-[8px] shrink-0">●</span>
          <span class="flex-1">${itemText}</span>
        </div>
      `)
      continue
    }

    // 6. Numbered Lists: `1. `
    const numMatch = trimmed.match(/^(\d+)\.\s+(.+)$/)
    if (numMatch) {
      const num = numMatch[1]
      const itemText = formatInline(numMatch[2])
      output.push(`
        <div class="flex items-start gap-2 ml-1 my-1 text-xs leading-relaxed text-slate-800 dark:text-slate-200">
          <span class="font-mono font-bold text-teal-600 dark:text-teal-400 text-[10.5px] shrink-0 mt-0.5">${num}.</span>
          <span class="flex-1">${itemText}</span>
        </div>
      `)
      continue
    }

    // 7. Empty line spacing
    if (trimmed === '') {
      output.push('<div class="h-2"></div>')
      continue
    }

    // 8. Regular paragraph
    output.push(`
      <p class="text-xs text-slate-800 dark:text-slate-200 leading-relaxed my-1">
        ${formatInline(trimmed)}
      </p>
    `)
  }

  // Handle unclosed code block if streaming was cut off
  if (inCodeBlock && codeBuffer.length > 0) {
    const escapedCode = escapeHtml(codeBuffer.join('\n'))
    output.push(`
      <div class="my-2 rounded-xl overflow-hidden border border-[#2D3748] bg-[#1A202C] text-[#E2E8F0] p-3 text-[11px] font-mono leading-relaxed">
        <code>${escapedCode}</code>
      </div>
    `)
  }

  return output.join('')
}
