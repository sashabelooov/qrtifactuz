# Museum Setup Workflow — Admin Panel

Follow this exact order. Each step depends on the previous one.

---

## Step-by-Step Order

```
┌─────────────────────────────────────────────────────────────┐
│                    ADMIN PANEL WORKFLOW                      │
│               /admin  →  add in this order                  │
└─────────────────────────────────────────────────────────────┘

STEP 1 ── Countries
┌──────────────────────────┐
│  Admin › Countries       │
│  ┌────────────────────┐  │
│  │ Name:  Uzbekistan  │  │
│  │ Code:  UZ          │  │
│  └────────────────────┘  │
│  [Save]                  │
└──────────────────────────┘
         │
         ▼
STEP 2 ── Cities  (requires Country from step 1)
┌──────────────────────────┐
│  Admin › Cities          │
│  ┌────────────────────┐  │
│  │ Country: Uzbekistan│  │
│  │ Name:    Tashkent  │  │
│  └────────────────────┘  │
│  [Save]                  │
└──────────────────────────┘
         │
         ▼
STEP 3 ── Museums  (requires City from step 2)
┌──────────────────────────────────────────┐
│  Admin › Museums                         │
│  ┌──────────────────────────────────┐    │
│  │ Name:     State History Museum   │    │
│  │ Slug:     state-history-museum   │    │
│  │ City:     Tashkent               │    │
│  │ Address:  ...                    │    │
│  │ Logo URL: (optional)             │    │
│  │ Active:   ✓                      │    │
│  └──────────────────────────────────┘    │
│  [Save]                                  │
└──────────────────────────────────────────┘
         │
         ▼
STEP 4 ── Halls  (requires Museum from step 3)
┌──────────────────────────────────────────┐
│  Admin › Halls                           │
│  ┌──────────────────────────────────┐    │
│  │ Museum:  State History Museum    │    │
│  │ Name:    Ancient History Hall    │    │
│  │ Floor:   1                       │    │
│  └──────────────────────────────────┘    │
│  [Save]                                  │
└──────────────────────────────────────────┘
         │
         ▼
STEP 5 ── Exhibits  (requires Museum + Hall)
┌──────────────────────────────────────────┐
│  Admin › Exhibits                        │
│  ┌──────────────────────────────────┐    │
│  │ Museum:  State History Museum    │    │
│  │ Hall:    Ancient History Hall    │    │
│  │ Slug:    golden-sword-exhibit    │    │
│  │ Status:  draft                   │    │
│  └──────────────────────────────────┘    │
│  [Save]                                  │
└──────────────────────────────────────────┘
         │
         ├─────────────────────────────────┐
         ▼                                 ▼
STEP 6a ── Translations            STEP 6b ── Media
(add 3x — uz / ru / en)            (images / video)
┌────────────────────────┐         ┌────────────────────────┐
│  Admin › Translations  │         │  Admin › Exhibit Media │
│  ┌──────────────────┐  │         │  ┌──────────────────┐  │
│  │ Exhibit: (slug)  │  │         │  │ Exhibit: (slug)  │  │
│  │ Language: uz     │  │         │  │ File: [Upload]   │  │
│  │ Title:   ...     │  │         │  │ Type: image      │  │
│  │ Descr:   ...     │  │         │  │ Cover: ✓         │  │
│  └──────────────────┘  │         │  │ Order: 0         │  │
│  [Save]  ×3 languages  │         │  └──────────────────┘  │
└────────────────────────┘         │  [Save]                │
                                   └────────────────────────┘
         │
         ▼
STEP 6c ── Audio Tracks  (one per language)
┌────────────────────────────────────────────┐
│  Admin › Audio Tracks                      │
│  ┌──────────────────────────────────────┐  │
│  │ Exhibit:          (slug)             │  │
│  │ Language:         uz                 │  │
│  │ File:             [Upload .mp3]      │  │
│  │ Duration (sec):   120                │  │
│  └──────────────────────────────────────┘  │
│  [Save]  ×3 languages                      │
└────────────────────────────────────────────┘
         │
         ▼
STEP 7 ── Publish  (change Exhibit status)
┌──────────────────────────────────────────┐
│  Admin › Exhibits › Edit exhibit         │
│  Status:  draft  →  published            │
│  [Save]                                  │
└──────────────────────────────────────────┘
         │
         ▼
      ✅ DONE — QR code auto-generates via Celery task
```

---

## Quick Reference Table

| Step | Section | Depends on |
|------|---------|-----------|
| 1 | Countries | — |
| 2 | Cities | Country |
| 3 | Museums | City |
| 4 | Halls | Museum |
| 5 | Exhibits | Museum + Hall |
| 6a | Translations (×3) | Exhibit |
| 6b | Exhibit Media | Exhibit |
| 6c | Audio Tracks (×3) | Exhibit |
| 7 | Set status → published | Exhibit |

---

## Notes

- **Slug** must be URL-safe (lowercase, hyphens only): `golden-sword-exhibit`
- **Cover image**: set `is_cover = true` on one media item per exhibit
- **Audio**: upload one `.mp3` per language (uz, ru, en)
- **QR code**: generated automatically after exhibit is published (Celery task)
- Always save a **Country** before trying to create a City — the dropdown will be empty otherwise
