# Settings Page Visual Layout

## Desktop View (>640px)

```
┌────────────────────────────────────────────────┐
│  ← Back to chat                                │
├────────────────────────────────────────────────┤
│                                                │
│                  SETTINGS PAGE                 │
│          Manage your profile, preferences,     │
│                  and data                      │
│                                                │
├────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────┐  │
│ │ PROFILE                                  │  │
│ ├──────────────────────────────────────────┤  │
│ │ Display name: [________________________]│  │
│ │                                          │  │
│ │ PREFERENCES                              │  │
│ │ Language:     [Vietnamese ▼]             │  │
│ │ Currency:     [VND ▼]                    │  │
│ │ Timezone:     [Asia/Ho_Chi_Minh ▼]      │  │
│ │                                          │  │
│ │              [Save settings]             │  │
│ └──────────────────────────────────────────┘  │
│                                                │
├────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────┐  │
│ │ DATA MANAGEMENT                          │  │
│ │ Backup, export, and restore your data   │  │
│ ├────────────────────┬─────────────────────┤  │
│ │ Export Data        │ Restore Data        │  │
│ │ Download JSON      │ Upload JSON from    │  │
│ │ backup of all data │ previous backup     │  │
│ │                    │                     │  │
│ │ [⬇ Export]         │ [⬆ Choose file]    │  │
│ ├────────────────────┴─────────────────────┤  │
│ │ 💡 Data is stored locally on your        │  │
│ │    device. Backup regularly to prevent   │  │
│ │    data loss.                            │  │
│ └──────────────────────────────────────────┘  │
│                                                │
└────────────────────────────────────────────────┘
```

## Mobile View (<640px)

```
┌──────────────────────────┐
│ ← Back to chat           │
├──────────────────────────┤
│   SETTINGS PAGE          │
│  Manage your profile...  │
├──────────────────────────┤
│ ┌──────────────────────┐ │
│ │ PROFILE              │ │
│ ├──────────────────────┤ │
│ │ Display name:        │ │
│ │ [__________________] │ │
│ │                      │ │
│ │ PREFERENCES          │ │
│ │ Language:            │ │
│ │ [Vietnamese ▼]       │ │
│ │ Currency:            │ │
│ │ [VND ▼]              │ │
│ │ Timezone:            │ │
│ │ [Asia/Ho_Chi_Minh ▼] │ │
│ │                      │ │
│ │  [Save settings]     │ │
│ └──────────────────────┘ │
│                          │
├──────────────────────────┤
│ ┌──────────────────────┐ │
│ │ DATA MANAGEMENT      │ │
│ │ Backup, export and   │ │
│ │ restore your data    │ │
│ ├──────────────────────┤ │
│ │ Export Data          │ │
│ │ Download JSON        │ │
│ │ backup of all data   │ │
│ │                      │ │
│ │   [⬇ Export]        │ │
│ ├──────────────────────┤ │
│ │ Restore Data         │ │
│ │ Upload JSON from     │ │
│ │ previous backup      │ │
│ │                      │ │
│ │ [⬆ Choose file]      │ │
│ ├──────────────────────┤ │
│ │ 💡 Data is stored    │ │
│ │    locally on your   │ │
│ │    device. Backup    │ │
│ │    regularly.        │ │
│ └──────────────────────┘ │
│                          │
└──────────────────────────┘
```

## Export Button Details

### Button States

**Normal State:**
```
┌────────────────────────────────┐
│         ⬇ Export              │  ← Primary Button (Blue)
└────────────────────────────────┘   width: 100%
```

**Hover State:**
```
┌────────────────────────────────┐
│         ⬇ Export              │  ← Darker blue
└────────────────────────────────┘   cursor: pointer
```

**Loading State:**
```
┌────────────────────────────────┐
│      Downloading…             │  ← Loading text
└────────────────────────────────┘   disabled: true
                                     opacity reduced
```

**After Export:**
```
Status Message: "Đã tải bản sao lưu."  ← Green success message
or
Status Message: "Backup failed."         ← Red error message
```

## Color Scheme

| Element | Color | Usage |
|---------|-------|-------|
| Export Button | `var(--primary)` | oklch(0.52 0.18 165) - Teal/Cyan |
| Button Hover | Darker teal | oklch(0.36 0.14 145) |
| Success Message | Green | oklch(0.50 0.18 145) |
| Error Message | Red | oklch(0.56 0.17 22) |
| Info Box | Yellow | oklch(0.68 0.15 72) |
| Background | Light gray | oklch(0.97 0.007 250) |
| Cards | White | #fff |
| Text | Dark gray | oklch(0.15 0.015 255) |
| Muted Text | Gray | oklch(0.60 0.01 250) |

## Interactive Flow

### Export Action

```
User sees:
  ↓
[⬇ Xuất / ⬇ Export] (Primary Button, full width)
  ↓ Click
Button disables, shows: [Đang tải… / Downloading…]
  ↓
File downloads as: finguard-backup-2024-05-28.json
  ↓
Status box appears: 
  ✓ "Đã tải bản sao lưu." (Vietnamese)
  ✓ "Backup downloaded." (English)
  ↓
Button re-enables after 2 seconds
```

### Restore Action

```
User sees:
  ↓
[⬆ Chọn file / ⬆ Choose file] (Ghost Button)
  ↓ Click
Hidden file input triggers
  ↓
User selects JSON file
  ↓
Confirmation dialog:
  "Khôi phục sẽ ghi đè dữ liệu hiện tại. Tiếp tục?"
  "Restore will overwrite current data. Continue?"
  ↓ User confirms
Data restored
  ↓
Status box appears:
  ✓ "Đã khôi phục dữ liệu." (Vietnamese)
  ✓ "Data restored." (English)
```

## Accessibility

- **Semantic HTML**: Proper labels, form elements
- **ARIA**: Role attributes where needed
- **Keyboard Navigation**: Tab through all inputs and buttons
- **Focus States**: Visible blue ring on focused elements
- **Color Contrast**: All text meets WCAG AA standards
- **Font Sizing**: Readable 14px base size
- **Touch Targets**: 44px minimum height on buttons

## Responsive Breakpoints

```css
/* Desktop: 640px+ */
- 2-column grid for export/restore
- 32px padding on container
- Full width optimized

/* Mobile: < 640px */
- Single column layout
- 20px padding on container
- Buttons stack vertically
- Increased touch-friendly spacing
```

## Performance Optimizations

- **Minimal Redraws**: CSS classes, no inline styles (except layout)
- **Lazy Loading**: Form data loaded on mount
- **Error Boundaries**: Status messages for failed exports
- **State Management**: Separate `exporting` state for UI feedback
- **File Naming**: Includes date (YYYY-MM-DD) for easy organization

