# FinGuard Settings Page Redesign

## Overview
The settings page has been completely redesigned with a modern, organized layout that prominently features the export/data management functionality. The page now has clear sectioning and improved visual hierarchy.

## Design Structure

### 1. **Page Layout**
- **Header**: Navigation back to chat + page title
- **Settings Container**: Max-width 600px centered container for optimal readability
- **Main Header Section**: Large title + subtitle describing purpose
- **Three Main Sections**: 
  - Profile
  - Preferences  
  - Data Management

### 2. **Profile Section**
- Display name input field
- Simple, focused form for basic user information
- Nested within a single form element for easy submission

### 3. **Preferences Section**
- **Language**: Vietnamese/English toggle (affects entire UI)
- **Currency**: 7 currency options (VND, USD, EUR, GBP, JPY, AUD, CAD)
- **Timezone**: 8 timezone options with major cities/regions
- All fields with consistent styling and hover states

### 4. **Data Management Section** ✨ (Featured)
The export button is **prominently placed** in a dedicated "Data Management" section with:

#### **Export Button**
- **Primary CTA**: Uses `button-primary` styling with export icon (⬇)
- **Full Width**: Takes up complete card width for prominence
- **Clear Labels**: Vietnamese "Xuất" / English "Export"
- **Loading State**: Shows "Đang tải…" / "Downloading…" during export
- **Instant Feedback**: Status message confirms download

#### **Layout**: Two-column grid on desktop
```
┌─────────────────────────────────────┐
│  Data Management Section            │
├──────────────────┬──────────────────┤
│  Export Data     │  Restore Data    │
│  (Primary)       │  (Ghost)         │
│  ⬇ Xuất         │  ⬆ Chọn file    │
└──────────────────┴──────────────────┘
```

#### **Features**:
- **Export Card**: 
  - Title + Description
  - Primary button for prominence
  - JSON format download with date stamp
  
- **Restore Card**:
  - Title + Description  
  - Ghost button (secondary action)
  - File input (hidden, triggered by button)

#### **Responsive**: Single column on mobile (<640px)

### 5. **Data Notice**
- Informational box at bottom of Data Management section
- Yellow/gold styling (pending color)
- Encourages regular backups
- Vietnamese + English support

## CSS Implementation

### New CSS Classes
```css
.settings-container      /* Max-width container with padding */
.settings-header         /* Title + subtitle section */
.settings-section        /* Card-style sections */
.section-header          /* Section titles */
.settings-form          /* Form wrapper */
.form-group             /* Input + label wrapper */
.form-label             /* Form labels */
.form-input             /* Input/select styling */
.data-actions           /* Grid layout for export/restore */
.action-card            /* Card for each action */
.action-header          /* Title + description in card */
.action-description     /* Secondary text in cards */
.data-notice            /* Information box */
.settings-ok            /* Success message styling */
.login-error            /* Error message styling */
```

### Design Tokens Used
- **Colors**: 
  - Primary: `var(--primary)` for export button
  - Text: `var(--text)`, `var(--text-muted)`
  - Surfaces: `var(--surface)`, `var(--surface-muted)`
  - Borders: `var(--border)`
- **Pending Color**: `oklch(0.68 0.15 72)` for notice box
- **Shadows**: Subtle borders, no drop shadows

### Responsive Design
- **Desktop (>640px)**: 2-column grid for export/restore
- **Mobile (<640px)**: Single column layout, optimized spacing
- **Padding**: 32px desktop → 20px mobile
- **Font sizes**: Consistent scaling

## Component Features

### Export Button
```tsx
<button
  type="button"
  className="button button-primary"
  onClick={() => void handleBackup()}
  disabled={exporting}
  style={{ width: "100%" }}
>
  {exporting
    ? isVi ? "Đang tải…" : "Downloading…"
    : isVi ? "⬇ Xuất" : "⬇ Export"}
</button>
```
- **Position**: Center of Data Management section, top card (left on desktop)
- **Accessibility**: Full-width button ensures easy clicking
- **Loading State**: Disabled + loading text
- **Emoji Icon**: Download arrow for visual clarity

### Restore Button (Secondary)
```tsx
<button
  type="button"
  className="button button-ghost"
  onClick={() => fileRef.current?.click()}
  style={{ width: "100%" }}
>
  {isVi ? "⬆ Chọn file" : "⬆ Choose file"}
</button>
```
- **Position**: Right of export button (below on mobile)
- **Style**: Ghost button (secondary action)
- **Icon**: Upload arrow
- **Behavior**: Triggers hidden file input

### Save Settings Button
```tsx
<button
  className="button button-primary"
  type="submit"
  disabled={saving}
  style={{ marginTop: 16, width: "100%" }}
>
  {saving ? (isVi ? "Đang lưu…" : "Saving…") : isVi ? "Lưu cài đặt" : "Save settings"}
</button>
```
- **Position**: Below Preferences section
- **Full Width**: Easy to tap/click
- **Loading State**: Managed with `saving` state

## Localization

All text is fully localized (Vietnamese/English):

| Element | Vietnamese | English |
|---------|-----------|---------|
| Page Title | "Cài đặt" | "Settings" |
| Subtitle | "Quản lý hồ sơ, tùy chọn và dữ liệu của bạn" | "Manage your profile, preferences, and data" |
| Data Section | "Quản lý dữ liệu" | "Data management" |
| Export | "Xuất dữ liệu" | "Export data" |
| Export Button | "⬇ Xuất" | "⬇ Export" |
| Loading | "Đang tải…" | "Downloading…" |
| Restore | "Khôi phục dữ liệu" | "Restore data" |
| Restore Button | "⬆ Chọn file" | "⬆ Choose file" |

## User Flow

1. **User navigates to `/settings`**
   - Profile section loads with user's current data
   - All preferences (language, currency, timezone) prefilled from DB

2. **User modifies settings**
   - Changes display name, language, currency, or timezone
   - Clicks "Lưu cài đặt" / "Save settings"
   - Status message confirms save
   - Page remains, ready for export

3. **User exports data** ✨
   - Scrolls to "Quản lý dữ liệu" section
   - Clicks prominent "⬇ Xuất" / "⬇ Export" button
   - File downloads as `finguard-backup-YYYY-MM-DD.json`
   - Status message confirms: "Đã tải bản sao lưu." / "Backup downloaded."

4. **User restores data** (optional)
   - Clicks "⬆ Chọn file" / "⬆ Choose file" button
   - Selects JSON backup file
   - Confirmation dialog appears (locale-aware)
   - Data restored or error shown

## Styling Highlights

- **Consistent Spacing**: 24px between sections, 18px between form groups
- **Clear Visual Hierarchy**: H1 title → H2 section headers → form labels
- **Focus States**: Blue ring on inputs (0 0 0 2px with 0.1 opacity)
- **Hover States**: Border color transitions on inputs
- **Error/Success**: Color-coded messages (green for success, red for error, yellow for info)
- **Cards**: Subtle borders, rounded corners (12px), clean white backgrounds

## Files Modified

1. **frontend/src/app/settings/page.tsx**
   - Restructured layout into three main sections
   - Added export loading state
   - Enhanced form organization
   - Full bilingual support

2. **frontend/src/app/globals.css** (Added ~195 lines)
   - `.settings-*` classes for page structure
   - `.form-*` classes for form styling
   - `.data-actions` grid layout
   - `.action-card` styling
   - `.data-notice` information box
   - Mobile responsive breakpoint

## Next Steps

- Test on all screen sizes (mobile, tablet, desktop)
- Verify export functionality works end-to-end
- Test locale switching and language change
- Consider adding tooltips for advanced options
- Monitor user feedback on data management features
