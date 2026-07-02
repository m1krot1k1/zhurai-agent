/**
 * Shared design tokens for Hermes branding parity between TUI (Ink) and Desktop (React/CSS vars).
 * Single source of truth for colors, spacing, typography to close visual gap.
 * Consumed by ui-tui/src/theme.ts (via re-export or direct import) and Desktop theme providers.
 *
 * Values taken from canonical default skin in skin_engine.py + DARK_THEME in ui-tui.
 */

export const COLORS = {
  primary: '#FFD700',      // banner_title, gold accent
  accent: '#FFBF00',       // banner_accent / ui_accent
  border: '#CD7F32',       // banner_border / input_rule
  text: '#FFF8DC',         // banner_text / prompt
  muted: '#B8860B',        // banner_dim (updated for readability in theme.ts)
  label: '#DAA520',        // ui_label / session_label
  ok: '#4caf50',
  error: '#ef5350',
  warn: '#ffa726',
  statusBg: '#1a1a2e',
  statusFg: '#C0C0C0',
  statusGood: '#8FBC8F',
  statusWarn: '#FFD700',
  statusBad: '#FF8C00',
  statusCritical: '#FF6B6B',
  selectionBg: '#333355',
  completionBg: '#1a1a2e',
  completionCurrentBg: '#333355',
} as const

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
} as const

export const TYPOGRAPHY = {
  fontFamily: 'monospace',
  fontSizeBase: 14,
  fontSizeSmall: 12,
} as const

export const BRAND = {
  name: 'Hermes Agent',
  icon: '⚕',
  promptSymbol: '❯',
} as const

export type DesignTokens = {
  colors: typeof COLORS
  spacing: typeof SPACING
  typography: typeof TYPOGRAPHY
  brand: typeof BRAND
}

export const DESIGN_TOKENS: DesignTokens = {
  colors: COLORS,
  spacing: SPACING,
  typography: TYPOGRAPHY,
  brand: BRAND,
}
