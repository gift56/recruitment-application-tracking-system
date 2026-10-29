# UI Registry

## Baseline — established 2026-10-29

| Property | Pattern |
|---|---|
| Page background | `bg-slate-50` |
| Card background | `bg-white` |
| Card border | `border border-slate-200` |
| Card radius | `rounded-2xl` |
| Control radius | `rounded-xl` |
| Primary text | `text-slate-900` |
| Secondary text | `text-slate-600` |
| Muted text | `text-slate-500` |
| Accent | `bg-indigo-600`, `text-indigo-700` |
| Focus | `focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600` |
| Card shadow | `shadow-sm` |
| Control shadow | `shadow-sm` |

The public home-page dark-indigo hero is an intentional page-specific variant. Recruiter pages use the shared light background and card treatment.

### Recruiter dashboard

File: `tracker/templates/tracker/recruiter_dashboard.html`  
Last updated: 2026-10-29

| Property | Class |
|---|---|
| Background | `bg-white` |
| Border | `border border-slate-200` |
| Border radius | `rounded-2xl` |
| Text — primary | `text-slate-900` |
| Text — secondary | `text-slate-600` |
| Spacing | `p-5` |
| Hover state | None |
| Shadow | `shadow-sm` |
| Accent usage | `text-indigo-600`, `bg-indigo-600` |

**Pattern notes:** Use small uppercase indigo section labels, semibold slate headings, and restrained white metric cards. Metric values use large slate text; buttons use the shared indigo action treatment.

### Recruiter forms

Files: `tracker/templates/tracker/login.html`, `tracker/templates/tracker/job_form.html`, and `tracker/forms.py`  
Last updated: 2026-10-29

| Property | Class |
|---|---|
| Background | `bg-white` |
| Border | `border border-slate-200` |
| Border radius | `rounded-2xl` |
| Text — primary | `text-slate-900` |
| Text — secondary | `text-slate-600` |
| Spacing | `p-6`, `space-y-5` / `space-y-6` |
| Hover state | `hover:bg-indigo-700` |
| Shadow | `shadow-sm` |
| Accent usage | `bg-indigo-600`, `focus:ring-indigo-200` |

**Pattern notes:** Form controls use `rounded-xl`, a slate border, white background, and an indigo focus ring. Keep labels visible, associate help/error text with controls, and render errors in rose.

### Application pipeline

File: `tracker/templates/tracker/application_pipeline.html`  
Last updated: 2026-10-29

| Property | Class |
|---|---|
| Background | `bg-white`, table header `bg-slate-50` |
| Border | `border-slate-200`, row separators `divide-slate-100` |
| Border radius | `rounded-2xl` surface, `rounded-xl` note panel |
| Text — primary | `text-slate-900` |
| Text — secondary | `text-slate-600` |
| Spacing | `px-5 py-4` |
| Hover state | `hover:bg-indigo-50` |
| Shadow | `shadow-sm` |
| Accent usage | `text-indigo-700`, `bg-indigo-600` |

**Pattern notes:** Retain the shared application-status badge colors from `tracker/templates/tracker/partials/status_badge.html`. Keep row actions compact but visibly focusable; the evaluation disclosure uses a slate panel with existing form-control styles.

### Recruiter job management

Files: `tracker/templates/tracker/recruiter_job_list.html` and `tracker/templates/tracker/job_confirm_delete.html`  
Last updated: 2026-10-29

| Property | Class |
|---|---|
| Background | `bg-white`, table header `bg-slate-50` |
| Border | `border-slate-200`, row separators `divide-slate-100` |
| Border radius | `rounded-2xl` surface, `rounded-xl` confirmation/actions |
| Text — primary | `text-slate-900` |
| Text — secondary | `text-slate-600` |
| Spacing | `px-5 py-4`, `p-6` |
| Hover state | `hover:bg-indigo-50`, `hover:bg-rose-800` for destructive action |
| Shadow | `shadow-sm` |
| Accent usage | Indigo for management/navigation; rose for delete action |

**Pattern notes:** Keep job data in a semantic, horizontally scrollable table on small screens. Destructive actions use rose styling and require a separate confirmation; application-linked jobs explain that they must be deactivated instead.

### Department form

File: `tracker/templates/tracker/department_form.html`  
Last updated: 2026-10-29

| Property | Class |
|---|---|
| Background | `bg-white` |
| Border | `border border-slate-200` |
| Border radius | `rounded-2xl` |
| Text — primary | `text-slate-900` |
| Text — secondary | `text-slate-600` |
| Spacing | `p-6`, `space-y-6` |
| Hover state | `hover:bg-indigo-700` |
| Shadow | `shadow-sm` |
| Accent usage | `text-indigo-600`, `bg-indigo-600` |

**Pattern notes:** Match the job form's visible labels, shared form controls, inline rose errors, and indigo primary action.
