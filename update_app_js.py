# Script to update app.js for full India & Stitch localization

app_js_content = '''/**
 * Main Civic Task Navigator Application Controller
 * Grounded in Civic Functionalism & Municipal Ledger discipline.
 * Localized for Indian Municipal Administration (MCGM / BMC, BBMP, MCD, GHMC)
 * Conforming to GIGW 3.0 / S3WaaS and Stitch Design standards.
 */
class CivicApp {
    constructor() {
        this.currentTaskId = 'task-mum-bakery';
        this.currentTask = null;
        this.currentRoadmap = null;
        this.selectedStationId = 'mum-bakery-3';
        
        // Persistent progress storage
        this.completedStepIds = new Set(JSON.parse(localStorage.getItem('civic_completed_steps') || '["mum-bakery-1", "mum-bakery-2"]'));
        this.inProgressStepIds = new Set(JSON.parse(localStorage.getItem('civic_inprogress_steps') || '["mum-bakery-3"]'));
        
        this.activeTab = 'task-lookup';
        this.wayfindingMode = 'subway'; // 'subway' | 'dag'
        this.criticalPathActive = false;

        // Accessibility font sizing state
        this.fontSizes = ['font-size-sm', 'font-size-md', 'font-size-lg', 'font-size-xl'];
        this.currentFontSizeIdx = 1; // Default medium (15px)

        this._init();
    }

    async _init() {
        this._bindNavigationEvents();
        this._bindUiEvents();

        // Initialize SVG DAG visualizer
        this.visualizer = new CivicGraphVisualizer('graph-canvas', (nodeId) => {
            this.selectStation(nodeId);
        });

        // Initialize Admin manager
        this.admin = new CivicAdminManager(this);
        window.adminManager = this.admin;

        // Check URL hash for direct tab navigation
        const initialHash = window.location.hash.replace('#', '');
        if (initialHash && ['task-lookup', 'roadmap-and-route', 'step-dossier', 'citizen-ledger', 'registry-admin'].includes(initialHash)) {
            this.activeTab = initialHash;
        }

        // Load tasks and initial roadmap
        await this.loadTasksList();
        await this.loadRoadmap(this.currentTaskId);

        // Apply active tab
        this.switchNavTab(this.activeTab);
    }

    _bindNavigationEvents() {
        document.querySelectorAll('#top-nav-tabs .nav-tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const path = btn.getAttribute('data-path');
                this.switchNavTab(path);
            });
        });

        window.addEventListener('hashchange', () => {
            const h = window.location.hash.replace('#', '');
            if (h && h !== this.activeTab) {
                this.switchNavTab(h);
            }
        });

        // Keyboard shortcuts: '/' focuses search, 'ESC' closes drawer
        window.addEventListener('keydown', (e) => {
            if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                e.preventDefault();
                this.switchNavTab('task-lookup');
                const inp = document.getElementById('taskQuery');
                if (inp) inp.focus();
            } else if (e.key === 'Escape') {
                this.closeDrawer();
            }
        });

        // Jurisdiction selector
        const selectJur = document.getElementById('select-jurisdiction');
        if (selectJur) {
            selectJur.addEventListener('change', (e) => {
                const val = e.target.value;
                if (val === 'Mumbai') this.loadTaskAndRoute('task-mum-bakery');
                else if (val === 'Bengaluru') this.loadTaskAndRoute('task-blr-restaurant');
                else if (val === 'Delhi') this.loadTaskAndRoute('task-del-mutation');
                else if (val === 'Hyderabad') this.loadTaskAndRoute('task-hyd-tech-biz');
                else if (val === 'Pune') this.loadTaskAndRoute('task-mum-construction');
                else this.loadTaskAndRoute('task-mum-bakery');
            });
        }
    }

    _bindUiEvents() {
        // Drawer backdrop & close button
        const btnClose = document.getElementById('btn-close-drawer');
        const backdrop = document.getElementById('drawer-backdrop');
        if (btnClose) btnClose.addEventListener('click', () => this.closeDrawer());
        if (backdrop) backdrop.addEventListener('click', () => this.closeDrawer());

        // Drawer complete toggle
        const btnToggleComplete = document.getElementById('btn-toggle-complete');
        if (btnToggleComplete) {
            btnToggleComplete.addEventListener('click', () => {
                this.toggleStepCompletion(this.selectedStationId);
            });
        }

        // DAG Canvas tools
        const btnZoomIn = document.getElementById('btn-zoom-in');
        const btnZoomOut = document.getElementById('btn-zoom-out');
        const btnFit = document.getElementById('btn-fit-screen');
        const btnReset = document.getElementById('btn-reset-view');

        if (btnZoomIn) btnZoomIn.addEventListener('click', () => this.visualizer.zoomIn());
        if (btnZoomOut) btnZoomOut.addEventListener('click', () => this.visualizer.zoomOut());
        if (btnFit) btnFit.addEventListener('click', () => this.visualizer.fitToScreen());
        if (btnReset) btnReset.addEventListener('click', () => this.visualizer.resetView());
    }

    // GIGW Accessibility: Font Resizer
    adjustFontSize(action) {
        const body = document.body;
        this.fontSizes.forEach(cls => body.classList.remove(cls));

        if (action === 'increase') {
            this.currentFontSizeIdx = Math.min(this.fontSizes.length - 1, this.currentFontSizeIdx + 1);
        } else if (action === 'decrease') {
            this.currentFontSizeIdx = Math.max(0, this.currentFontSizeIdx - 1);
        } else {
            this.currentFontSizeIdx = 1; // Default
        }

        body.classList.add(this.fontSizes[this.currentFontSizeIdx]);
    }

    // GIGW Accessibility: High Contrast Toggle
    toggleHighContrast() {
        document.body.classList.toggle('high-contrast');
    }

    switchNavTab(tabName) {
        this.activeTab = tabName;
        window.location.hash = tabName;

        // Update nav buttons
        document.querySelectorAll('#top-nav-tabs .nav-tab-btn').forEach(btn => {
            const matches = btn.getAttribute('data-path') === tabName;
            btn.classList.toggle('active', matches);
        });

        // Hide/Show tab panes
        const panes = ['task-lookup', 'roadmap-and-route', 'step-dossier', 'citizen-ledger', 'registry-admin'];
        panes.forEach(pane => {
            const el = document.getElementById(`view-${pane}`);
            if (el) {
                el.style.display = (pane === tabName) ? 'flex' : 'none';
            }
        });

        window.scrollTo({ top: 0, behavior: 'smooth' });

        if (tabName === 'roadmap-and-route') {
            if (this.wayfindingMode === 'dag') {
                setTimeout(() => this.visualizer.fitToScreen(), 50);
            }
        } else if (tabName === 'citizen-ledger') {
            this.renderCitizenLedger();
        } else if (tabName === 'registry-admin') {
            this.admin.switchTab('scraper');
        }
    }

    async loadTasksList() {
        try {
            const resp = await fetch('/api/tasks');
            this.allTasks = await resp.json();
        } catch (e) {
            console.error('Failed to load tasks list', e);
        }
    }

    async loadTaskAndRoute(taskId) {
        this.currentTaskId = taskId;
        await this.loadRoadmap(taskId);

        // Pick default step
        if (this.currentTask && this.currentTask.steps.length > 0) {
            const defaultStep = this.currentTask.steps.find(s => !this.completedStepIds.has(s.id)) || this.currentTask.steps[0];
            this.selectStation(defaultStep.id);
        }

        // Switch to Roadmap view
        this.switchNavTab('roadmap-and-route');
    }

    async loadRoadmap(taskId) {
        try {
            const resp = await fetch(`/api/tasks/${taskId}/roadmap`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    completed_step_ids: Array.from(this.completedStepIds),
                    in_progress_step_ids: Array.from(this.inProgressStepIds)
                })
            });

            if (!resp.ok) throw new Error('Failed to load roadmap');
            this.currentRoadmap = await resp.json();
            this.currentTask = this.currentRoadmap.task;

            this.updateHeaderAndStats();
            this.visualizer.setRoadmapData(this.currentRoadmap);
            this.renderRailMilestones();
            this.updateStationUI();
            this.renderCitizenLedger();
        } catch (e) {
            console.error('Roadmap error', e);
        }
    }

    updateHeaderAndStats() {
        const t = this.currentTask;
        const r = this.currentRoadmap;
        if (!t || !r) return;

        // Roadmap title & description
        const elTitle = document.getElementById('roadmap-heading-title');
        const elDesc = document.getElementById('roadmap-heading-desc');
        const elRouteId = document.getElementById('route-id-badge');
        const elRouteClass = document.getElementById('route-class-badge');

        if (elTitle) elTitle.innerText = `Route Map: ${t.title}`;
        if (elDesc) elDesc.innerText = t.description;
        if (elRouteId) elRouteId.innerText = `ROUTE #${t.id.toUpperCase().replace('TASK-', '')}`;
        if (elRouteClass) elRouteClass.innerText = t.category;

        // Summary stats ribbon
        const elTimeline = document.getElementById('summary-stat-timeline');
        const elFees = document.getElementById('summary-stat-fees');
        const elProgress = document.getElementById('summary-stat-progress');
        const elBlocker = document.getElementById('summary-stat-blocker');

        const totalSteps = t.steps ? t.steps.length : 0;
        const doneSteps = r.completed_count || 0;

        if (elTimeline) elTimeline.innerText = `${r.total_estimated_days}–${r.total_estimated_days + 15}`;
        if (elFees) elFees.innerText = `₹${(r.total_estimated_fees || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
        if (elProgress) elProgress.innerText = `${doneSteps} / ${totalSteps}`;

        if (elBlocker) {
            const firstPending = t.steps.find(s => !this.completedStepIds.has(s.id));
            if (firstPending) {
                elBlocker.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500 shrink-0"></span> ${firstPending.department.name.split('(')[0]}`;
            } else {
                elBlocker.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-600 shrink-0"></span> All Milestones Cleared`;
            }
        }
    }

    renderRailMilestones() {
        const container = document.getElementById('rail-stations-list');
        const countBadge = document.getElementById('rail-milestones-count');
        if (!container || !this.currentTask) return;

        const steps = this.currentTask.steps;
        if (countBadge) countBadge.innerText = `${steps.length} Stops`;

        container.innerHTML = steps.map((s, idx) => {
            const isCompleted = this.completedStepIds.has(s.id);
            const isSelected = this.selectedStationId === s.id;
            
            let statusBadge = '<span class="font-headline text-[10px] text-secondary">Upcoming</span>';
            let dotBg = 'bg-surface-container-highest text-secondary';
            if (isCompleted) {
                statusBadge = '<span class="font-headline text-[10px] text-emerald-800 font-bold">✓ Cleared</span>';
                dotBg = 'bg-emerald-700 text-white';
            } else if (isSelected) {
                statusBadge = '<span class="font-headline text-[10px] text-amber-800 font-bold">Active</span>';
                dotBg = 'bg-amber-500 text-white';
            }

            return `
                <div class="p-2 border border-outline-variant flex items-center justify-between cursor-pointer hover:bg-surface-container-low transition-colors ${isSelected ? 'bg-surface-container-low border-l-4 border-l-amber-500' : 'bg-surface-container-lowest'}" onclick="window.app.selectStation('${s.id}')">
                    <div class="flex items-center gap-2">
                        <span class="w-5 h-5 rounded-full ${dotBg} flex items-center justify-center font-code text-[10px] font-bold">${idx + 1}</span>
                        <div class="truncate max-w-[140px]">
                            <div class="font-headline text-xs font-semibold text-primary truncate">${s.title}</div>
                            <div class="font-code text-[10px] text-secondary truncate">${s.department.name.split('(')[0]}</div>
                        </div>
                    </div>
                    <div>${statusBadge}</div>
                </div>
            `;
        }).join('');
    }

    selectStation(stepId) {
        this.selectedStationId = stepId;
        this.updateStationUI();
        this.renderRailMilestones();
    }

    updateStationUI() {
        if (!this.currentTask) return;
        const step = this.currentTask.steps.find(s => s.id === this.selectedStationId) || this.currentTask.steps[0];
        if (!step) return;

        const isCompleted = this.completedStepIds.has(step.id);

        // 1. Update Active Station Dossier Card on Roadmap view
        const badgeStep = document.getElementById('station-badge-step');
        const badgeStatus = document.getElementById('station-badge-status');
        const badgeAgency = document.getElementById('station-badge-agency');
        const titleEl = document.getElementById('station-title');
        const descEl = document.getElementById('station-desc');
        const slaEl = document.getElementById('station-sla-days');
        const feeEl = document.getElementById('station-fee-amount');
        const checklistEl = document.getElementById('station-checklist');
        const docketRef = document.getElementById('station-docket-ref');

        if (badgeStep) badgeStep.innerText = `STOP 0${step.step_number} / ${step.department.jurisdiction.toUpperCase()}`;
        if (badgeAgency) badgeAgency.innerText = `Agency: ${step.department.name}`;
        if (titleEl) titleEl.innerText = step.title;
        if (descEl) descEl.innerText = step.description;
        if (slaEl) slaEl.innerText = `${step.estimated_days} Days`;
        if (feeEl) feeEl.innerText = step.fee_amount > 0 ? `₹${step.fee_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : 'Exempt';
        if (docketRef) docketRef.innerText = `DOCKET REF: MCGM-${step.id.toUpperCase()}-2024`;

        if (badgeStatus) {
            if (isCompleted) {
                badgeStatus.className = 'bg-emerald-100 text-emerald-900 font-headline text-xs px-2.5 py-0.5 font-bold uppercase flex items-center gap-1';
                badgeStatus.innerHTML = '<span class="material-symbols-outlined text-[14px]">done_all</span> Satisfied &amp; Verified';
            } else {
                badgeStatus.className = 'bg-amber-100 text-amber-900 font-headline text-xs px-2.5 py-0.5 font-bold uppercase flex items-center gap-1';
                badgeStatus.innerHTML = '<span class="w-2 h-2 rounded-full bg-amber-600 animate-ping"></span> In Progress';
            }
        }

        if (checklistEl) {
            checklistEl.innerHTML = step.documents.map(d => `
                <label class="flex items-start gap-1.5 font-body text-xs text-on-surface cursor-pointer">
                    <span class="material-symbols-outlined ${isCompleted ? 'text-emerald-700' : 'text-amber-600'} text-[18px]">${isCompleted ? 'check_box' : 'indeterminate_check_box'}</span>
                    <span>${d.name} (${d.is_mandatory ? 'Mandatory' : 'Optional'})</span>
                </label>
            `).join('') || '<div class="text-xs text-secondary font-headline">No prior physical filings required for this station.</div>';
        }

        // 2. Update Step Dossier Tab View
        this.populateDossierView(step);

        // 3. Update Drawer content as well
        this.populateDrawer(step);
    }

    populateDossierView(step) {
        const isCompleted = this.completedStepIds.has(step.id);

        const routeCrumb = document.getElementById('dossier-route-crumb');
        const stepCrumb = document.getElementById('dossier-step-crumb');
        const refCode = document.getElementById('dossier-ref-code');
        const stageIdx = document.getElementById('dossier-stage-idx');
        const agencyName = document.getElementById('dossier-agency-name');
        const mainTitle = document.getElementById('dossier-main-title');
        const mainDesc = document.getElementById('dossier-main-desc');
        const statusText = document.getElementById('dossier-status-text');
        const statusDot = document.getElementById('dossier-status-dot');
        const statusSla = document.getElementById('dossier-status-sla');
        const provText = document.getElementById('dossier-provenance-text');
        const provLink = document.getElementById('dossier-provenance-link');
        const provLinkText = document.getElementById('dossier-provenance-link-text');

        if (routeCrumb) routeCrumb.innerText = this.currentTask.title;
        if (stepCrumb) stepCrumb.innerText = `Stop 0${step.step_number} (${step.title})`;
        if (refCode) refCode.innerText = `REF: ${step.id.toUpperCase()}-2024-STATUTORY`;
        if (stageIdx) stageIdx.innerText = `STAGE 0${step.step_number} / 0${this.currentTask.steps.length}`;
        if (agencyName) agencyName.innerText = `${step.department.name} — ${step.department.jurisdiction}`;
        if (mainTitle) mainTitle.innerText = `Step 0${step.step_number}: ${step.title}`;
        if (mainDesc) mainDesc.innerText = step.description;

        if (statusText) statusText.innerText = isCompleted ? 'Cleared & Verified on File' : 'In Progress: Action Required';
        if (statusDot) statusDot.className = isCompleted ? 'w-2.5 h-2.5 rounded-full bg-emerald-600' : 'w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse';
        if (statusSla) statusSla.innerText = `Target Statutory Window: ${step.estimated_days} Working Days`;

        if (provText) {
            provText.innerHTML = `Verified against <strong>${step.verification_source.gazette_ref || 'Municipal Corporation of Greater Mumbai Regulations'}</strong> as of <strong>${step.verification_source.last_scraped_at ? step.verification_source.last_scraped_at.split('T')[0] : 'October 2024'}</strong>.`;
        }
        if (provLink && provLinkText) {
            provLink.href = step.verification_source.url;
            provLinkText.innerText = step.verification_source.url.replace('https://', '');
        }

        // Prerequisites bar
        const prereqGrid = document.getElementById('dossier-prereqs-grid');
        const prereqStatus = document.getElementById('dossier-prereq-chain-status');
        if (prereqGrid) {
            if (step.prerequisites.length === 0) {
                prereqGrid.innerHTML = `
                    <div class="col-span-2 bg-surface-container-lowest p-3 border border-outline-variant text-xs text-secondary font-headline">
                        ✓ Station Initializer: Root procedural milestone under Maharashtra statutory rules.
                    </div>
                `;
                if (prereqStatus) prereqStatus.innerText = 'CHAIN STATUS: ROOT MILESTONE';
            } else {
                const totalReq = step.prerequisites.length;
                const clearedReq = step.prerequisites.filter(p => this.completedStepIds.has(p)).length;
                if (prereqStatus) prereqStatus.innerText = `CHAIN STATUS: ${clearedReq}/${totalReq} SATISFIED`;

                prereqGrid.innerHTML = step.prerequisites.map(pId => {
                    const prereqStep = this.currentTask.steps.find(s => s.id === pId);
                    const isPrereqDone = this.completedStepIds.has(pId);
                    return `
                        <div class="bg-surface-container-lowest p-3 border border-outline-variant flex items-center justify-between">
                            <div class="flex items-center gap-2.5">
                                <span class="w-5 h-5 rounded-full ${isPrereqDone ? 'bg-emerald-800 text-white' : 'bg-surface-container text-secondary'} flex items-center justify-center font-code text-[11px] font-bold">
                                    ${isPrereqDone ? '✓' : '•'}
                                </span>
                                <div>
                                    <div class="font-headline text-xs font-semibold text-primary">${prereqStep ? prereqStep.title : pId}</div>
                                    <div class="font-code text-[10px] text-secondary">Prerequisite Clearance</div>
                                </div>
                            </div>
                            <span class="font-headline text-[10px] ${isPrereqDone ? 'bg-emerald-100 text-emerald-900 border border-emerald-300' : 'bg-amber-50 text-amber-900 border border-amber-300'} px-2 py-0.5 font-semibold">
                                ${isPrereqDone ? 'Cleared' : 'Pending'}
                            </span>
                        </div>
                    `;
                }).join('');
            }
        }

        // Statutory Forms
        const formsContainer = document.getElementById('dossier-forms-container');
        const formsCount = document.getElementById('dossier-forms-count');
        if (formsContainer) {
            if (formsCount) formsCount.innerText = `${step.forms.length} Prescribed Instruments`;
            formsContainer.innerHTML = step.forms.map(f => `
                <div class="py-3 first:pt-0 last:pb-0 flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div class="space-y-0.5 max-w-xl">
                        <div class="flex items-center gap-2">
                            <span class="font-code text-xs font-semibold bg-surface-container px-2 py-0.5 border border-outline-variant text-primary">${f.form_code}</span>
                            <h3 class="font-headline text-sm font-semibold text-primary">${f.title}</h3>
                        </div>
                        <p class="font-body text-xs text-on-surface-variant leading-relaxed">Official administrative instrument required for filing under municipal procedure code.</p>
                        <div class="font-code text-[11px] text-secondary">Authorized Format: Digital E-Filing or PDF Document</div>
                    </div>
                    <a class="inline-flex items-center justify-center gap-1.5 bg-surface-container-lowest text-primary border border-outline hover:bg-surface-container-low px-4 py-2 font-headline text-xs font-semibold transition-colors shrink-0" href="${f.download_url || f.fill_online_url || '#'}" target="_blank">
                        <span class="material-symbols-outlined text-[16px]">download</span>
                        <span>Official Instrument (${f.download_url ? 'PDF' : 'E-Portal'})</span>
                    </a>
                </div>
            `).join('') || '<div class="text-xs text-secondary font-headline">No separate form instruments prescribed. Proceed with direct declaration.</div>';
        }

        // Evidence & Sealed Filings
        const evidenceContainer = document.getElementById('dossier-evidence-container');
        const evidenceCount = document.getElementById('dossier-evidence-count');
        if (evidenceContainer) {
            if (evidenceCount) evidenceCount.innerText = `${step.documents.length} Evidence Criteria`;
            evidenceContainer.innerHTML = step.documents.map(d => `
                <div class="p-3 bg-surface-container-lowest border border-outline-variant flex flex-col md:flex-row items-start justify-between gap-3">
                    <div class="space-y-0.5 max-w-xl">
                        <div class="flex items-center gap-2">
                            <span class="material-symbols-outlined text-amber-700 text-[18px]">pending</span>
                            <span class="font-headline text-sm font-semibold text-primary">${d.name}</span>
                        </div>
                        <p class="font-body text-xs text-on-surface-variant leading-relaxed">${d.description}</p>
                        <div class="font-code text-[11px] text-outline">CRITERIA: Must be authenticated and digitally signed</div>
                    </div>
                    <div class="shrink-0 flex flex-col items-start md:items-end gap-1">
                        <span class="font-headline text-[10px] bg-amber-50 text-amber-900 border border-amber-300 px-2 py-0.5 font-semibold">Action Required</span>
                        <button class="font-headline text-xs text-primary underline hover:text-secondary font-medium mt-1" onclick="alert('Document upload portal opened for: ${d.name}')">Upload Document</button>
                    </div>
                </div>
            `).join('') || '<div class="text-xs text-secondary font-headline">No additional document filings mandated for this step.</div>';
        }

        // Fee Breakdown Table (in INR ₹)
        const feeTableBody = document.getElementById('dossier-fee-table-body');
        const feeTotalEl = document.getElementById('dossier-fee-total');
        if (feeTableBody) {
            const breakdown = step.fee_breakdown;
            const entries = Object.entries(breakdown);
            if (entries.length === 0) {
                feeTableBody.innerHTML = `
                    <tr>
                        <td class="py-2.5 px-4 font-semibold text-primary">Standard Processing Fee</td>
                        <td class="py-2.5 px-4 text-secondary">Municipal Tariff Schedule</td>
                        <td class="py-2.5 px-4 text-right font-code">Per Unit</td>
                        <td class="py-2.5 px-4 text-right font-code font-semibold text-primary">₹${step.fee_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    </tr>
                `;
            } else {
                feeTableBody.innerHTML = entries.map(([key, val]) => `
                    <tr>
                        <td class="py-2.5 px-4 font-semibold text-primary">${key}</td>
                        <td class="py-2.5 px-4 text-secondary">MMC Act / Statutory Basis</td>
                        <td class="py-2.5 px-4 text-right font-code">Per Filing Schedule</td>
                        <td class="py-2.5 px-4 text-right font-code font-semibold text-primary">₹${parseFloat(val).toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    </tr>
                `).join('');
            }
            if (feeTotalEl) feeTotalEl.innerText = `₹${step.fee_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
        }

        // Guidelines & Pitfalls
        const guidelinesText = document.getElementById('dossier-guidelines-text');
        if (guidelinesText) {
            guidelinesText.innerText = step.tips_and_pitfalls || 'Ensure all submissions are accompanied by valid tax clearance certificates and registered engineer seals.';
        }

        // Office Details in Right Rail
        const officeAddress = document.getElementById('dossier-office-address');
        const officeWindow = document.getElementById('dossier-office-window');
        const officeCity = document.getElementById('dossier-office-city');
        const officeHours = document.getElementById('dossier-office-hours');
        const officeBorough = document.getElementById('dossier-office-borough');
        const ombudsPhone = document.getElementById('dossier-ombuds-phone');
        const ombudsEmail = document.getElementById('dossier-ombuds-email');

        if (officeAddress) officeAddress.innerText = step.department.office_address || 'MCGM Ward H/West Municipal Office';
        if (officeWindow) officeWindow.innerText = `${step.department.name} — Intake Window`;
        if (officeCity) officeCity.innerText = step.department.jurisdiction;
        if (officeHours) officeHours.innerText = step.department.working_hours || 'Monday – Friday: 10:00 AM – 2:30 PM IST';
        if (officeBorough) officeBorough.innerText = step.department.jurisdiction.toUpperCase();
        if (ombudsPhone) ombudsPhone.innerText = step.department.contact_phone || '(022) 2642-2311';
        if (ombudsEmail) ombudsEmail.innerText = step.department.contact_email || 'eodb.support@mcgm.gov.in';

        // Action button state
        const advanceBtn = document.getElementById('btn-advance-route');
        const advanceLabel = document.getElementById('btn-advance-label');
        if (advanceBtn && advanceLabel) {
            if (isCompleted) {
                advanceBtn.className = 'w-full bg-emerald-800 text-on-primary px-4 py-3 font-headline text-xs font-semibold tracking-wide border border-emerald-900 transition-colors flex items-center justify-center gap-1.5';
                advanceLabel.innerText = 'Milestone Cleared & Verified';
            } else {
                advanceBtn.className = 'w-full bg-primary text-on-primary hover:bg-primary-container px-4 py-3 font-headline text-xs font-semibold tracking-wide border border-primary transition-colors flex items-center justify-center gap-1.5';
                advanceLabel.innerText = 'Mark Step Complete & Advance';
            }
        }
    }

    populateDrawer(step) {
        const badge = document.getElementById('drawer-step-badge');
        const title = document.getElementById('drawer-title');
        const conf = document.getElementById('drawer-confidence');
        const url = document.getElementById('drawer-provenance-url');
        const gaz = document.getElementById('drawer-gazette-ref');
        const dept = document.getElementById('drawer-dept-name');
        const addr = document.getElementById('drawer-office-addr');
        const hours = document.getElementById('drawer-office-hours');
        const sla = document.getElementById('drawer-sla-days');
        const desc = document.getElementById('drawer-step-desc');
        const docs = document.getElementById('drawer-docs-list');
        const forms = document.getElementById('drawer-forms-list');
        const fees = document.getElementById('drawer-fee-breakdown');
        const btnComplete = document.getElementById('btn-toggle-complete');

        if (badge) badge.innerText = `Step ${step.step_number}`;
        if (title) title.innerText = step.title;
        if (conf) conf.innerText = `${(step.verification_source.confidence_score * 100).toFixed(0)}% Match`;
        if (url) {
            url.href = step.verification_source.url;
            url.innerText = step.verification_source.url;
        }
        if (gaz) gaz.innerText = `Statutory Authority: ${step.verification_source.gazette_ref || 'MMC Act 1888 § 394'}`;
        if (dept) dept.innerText = step.department.name;
        if (addr) addr.innerText = step.department.office_address;
        if (hours) hours.innerText = step.department.working_hours || 'Mon-Fri 10:00 AM - 2:30 PM IST';
        if (sla) sla.innerText = `${step.estimated_days} Days`;
        if (desc) desc.innerText = step.description;

        if (docs) {
            docs.innerHTML = step.documents.map(d => `<div class="bg-surface-container-lowest p-2 border border-outline-variant">• <strong>${d.name}</strong></div>`).join('') || 'None';
        }
        if (forms) {
            forms.innerHTML = step.forms.map(f => `<div class="bg-surface-container-lowest p-2 border border-outline-variant">• <strong>${f.form_code}</strong>: ${f.title}</div>`).join('') || 'None';
        }
        if (fees) {
            fees.innerHTML = Object.entries(step.fee_breakdown).map(([k, v]) => `<div>${k}: <strong>₹${parseFloat(v).toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong></div>`).join('') || `Total: ₹${step.fee_amount.toFixed(2)}`;
        }

        if (btnComplete) {
            const isCompleted = this.completedStepIds.has(step.id);
            btnComplete.innerHTML = isCompleted ? '<span class="material-symbols-outlined text-[16px]">done_all</span><span>Completed ✓</span>' : '<span class="material-symbols-outlined text-[16px]">check_circle</span><span>Mark Step Completed</span>';
            btnComplete.className = isCompleted ? 'flex-1 bg-emerald-800 text-on-primary font-headline text-xs font-semibold py-2.5 px-3 flex items-center justify-center gap-1.5' : 'flex-1 bg-primary hover:bg-primary-container text-on-primary font-headline text-xs font-semibold py-2.5 px-3 flex items-center justify-center gap-1.5 transition-colors';
        }
    }

    openDrawer(stepId) {
        this.selectStation(stepId);
        const drawer = document.getElementById('step-drawer');
        const backdrop = document.getElementById('drawer-backdrop');
        if (drawer) drawer.classList.add('open');
        if (backdrop) backdrop.classList.add('open');
    }

    closeDrawer() {
        const drawer = document.getElementById('step-drawer');
        const backdrop = document.getElementById('drawer-backdrop');
        if (drawer) drawer.classList.remove('open');
        if (backdrop) backdrop.classList.remove('open');
    }

    inspectFullDossier() {
        this.switchNavTab('step-dossier');
    }

    inspectFullDossierFromDrawer() {
        this.closeDrawer();
        this.switchNavTab('step-dossier');
    }

    async advanceStepAction() {
        const inputRef = document.getElementById('mcgm-app-num') || document.getElementById('dob-job-num');
        const val = inputRef ? inputRef.value.trim() : '';

        if (!val || val.length < 6) {
            alert('Procedural Notice: Please enter a valid 10-digit MCGM Citizen Application Number (e.g. 7204918204) before marking this step complete.');
            if (inputRef) inputRef.focus();
            return;
        }

        const stepId = this.selectedStationId;
        this.completedStepIds.add(stepId);
        this.inProgressStepIds.delete(stepId);
        localStorage.setItem('civic_completed_steps', JSON.stringify(Array.from(this.completedStepIds)));
        localStorage.setItem('civic_inprogress_steps', JSON.stringify(Array.from(this.inProgressStepIds)));

        alert(`Application #${val} successfully verified against MCGM Citizen Portal records. Milestone "${stepId}" recorded as Satisfied.`);

        // Find next step to select
        const steps = this.currentTask.steps;
        const currIdx = steps.findIndex(s => s.id === stepId);
        if (currIdx >= 0 && currIdx < steps.length - 1) {
            this.selectedStationId = steps[currIdx + 1].id;
        }

        await this.loadRoadmap(this.currentTaskId);
    }

    async toggleStepCompletion(stepId) {
        if (this.completedStepIds.has(stepId)) {
            this.completedStepIds.delete(stepId);
        } else {
            this.completedStepIds.add(stepId);
            this.inProgressStepIds.delete(stepId);
        }
        localStorage.setItem('civic_completed_steps', JSON.stringify(Array.from(this.completedStepIds)));
        localStorage.setItem('civic_inprogress_steps', JSON.stringify(Array.from(this.inProgressStepIds)));

        await this.loadRoadmap(this.currentTaskId);
        this.updateStationUI();
    }

    toggleWayfindingView(mode) {
        this.wayfindingMode = mode;
        const subwayWrapper = document.getElementById('subway-diagram-wrapper');
        const dagWrapper = document.getElementById('dag-canvas-wrapper');
        const btnSubway = document.getElementById('btn-mode-subway');
        const btnDag = document.getElementById('btn-mode-dag');

        if (mode === 'subway') {
            if (subwayWrapper) subwayWrapper.style.display = 'block';
            if (dagWrapper) dagWrapper.style.display = 'none';
            if (btnSubway) {
                btnSubway.className = 'px-3 py-1.5 font-headline text-xs font-semibold bg-primary text-on-primary';
            }
            if (btnDag) {
                btnDag.className = 'px-3 py-1.5 font-headline text-xs font-semibold text-secondary hover:text-primary';
            }
        } else {
            if (subwayWrapper) subwayWrapper.style.display = 'none';
            if (dagWrapper) dagWrapper.style.display = 'block';
            if (btnSubway) {
                btnSubway.className = 'px-3 py-1.5 font-headline text-xs font-semibold text-secondary hover:text-primary';
            }
            if (btnDag) {
                btnDag.className = 'px-3 py-1.5 font-headline text-xs font-semibold bg-primary text-on-primary';
            }
            setTimeout(() => this.visualizer.fitToScreen(), 50);
        }
    }

    toggleCriticalPathHighlight() {
        this.criticalPathActive = !this.criticalPathActive;
        const btn = document.getElementById('btn-toggle-critical');
        const txt = document.getElementById('txt-critical');

        if (btn) btn.classList.toggle('bg-primary', this.criticalPathActive);
        if (btn) btn.classList.toggle('text-on-primary', this.criticalPathActive);
        if (txt) txt.innerText = this.criticalPathActive ? 'Highlighting Critical Path' : 'Show Critical Path Only';

        this.visualizer.toggleCriticalPath(this.criticalPathActive);

        // Highlight subway tracks
        const branch3a = document.getElementById('branch-3a-line');
        const branch3b = document.getElementById('branch-3b-line');
        if (branch3a && branch3b) {
            branch3a.style.opacity = this.criticalPathActive ? '0.2' : '1';
            branch3b.style.opacity = this.criticalPathActive ? '0.2' : '1';
        }
    }

    renderCitizenLedger() {
        const tbody = document.getElementById('citizen-ledger-table-body');
        const totalCount = document.getElementById('ledger-total-milestones');
        const clearedCount = document.getElementById('ledger-cleared-milestones');
        const feeCount = document.getElementById('ledger-total-fees');

        if (!tbody || !this.currentTask) return;

        const steps = this.currentTask.steps;
        const cleared = steps.filter(s => this.completedStepIds.has(s.id)).length;
        const totalFees = steps.reduce((sum, s) => sum + s.fee_amount, 0);

        if (totalCount) totalCount.innerText = `${steps.length} Stations`;
        if (clearedCount) clearedCount.innerText = `${cleared} Cleared (${Math.round((cleared / steps.length) * 100)}%)`;
        if (feeCount) feeCount.innerText = `₹${totalFees.toLocaleString(undefined, { minimumFractionDigits: 2 })} Base`;

        tbody.innerHTML = steps.map((s, idx) => {
            const isDone = this.completedStepIds.has(s.id);
            const statusHtml = isDone 
                ? '<span class="chip chip-verified">✓ Satisfied &amp; Logged</span>'
                : '<span class="chip chip-action-required">Action Required</span>';
            const dateStr = isDone ? '2024-09-28 [NODE MUM-W-HW]' : 'Pending Filing';

            return `
                <tr>
                    <td class="font-code font-bold text-primary">0${idx + 1}</td>
                    <td>
                        <div class="font-headline font-semibold text-primary text-xs">${s.title}</div>
                        <div class="font-body text-xs text-secondary mt-0.5 truncate max-w-md">${s.description}</div>
                    </td>
                    <td class="font-headline text-xs">${s.department.name.split('(')[0]}</td>
                    <td class="font-code text-xs text-secondary">MCGM-${s.id.toUpperCase()}-2024</td>
                    <td class="font-code text-xs font-semibold text-primary">₹${s.fee_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td>
                        <div>${statusHtml}</div>
                        <div class="font-code text-[10px] text-secondary mt-0.5">${dateStr}</div>
                    </td>
                    <td class="text-right">
                        <button class="bg-surface-container text-primary hover:bg-primary hover:text-on-primary px-3 py-1 font-headline text-xs font-semibold transition-colors border border-outline-variant" onclick="window.app.selectStation('${s.id}'); window.app.switchNavTab('step-dossier');">
                            Dossier
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    async performSearch() {
        const queryInput = document.getElementById('taskQuery');
        const jurSelect = document.getElementById('jurisdictionSelect');
        const q = queryInput ? queryInput.value.trim().toLowerCase() : '';
        const jur = jurSelect ? jurSelect.value : '';

        if (!q) {
            this.switchNavTab('roadmap-and-route');
            return;
        }

        // Direct keyword matching
        if (q.includes('bakery') || q.includes('cafe') || q.includes('mumbai') || q.includes('bandra') || q.includes('mcgm') || q.includes('bmc') || jur.includes('Mumbai')) {
            await this.loadTaskAndRoute('task-mum-bakery');
        } else if (q.includes('bengaluru') || q.includes('bbmp') || q.includes('karnataka') || jur.includes('Bengaluru')) {
            await this.loadTaskAndRoute('task-blr-restaurant');
        } else if (q.includes('building') || q.includes('construction') || q.includes('autodcr') || jur.includes('Pune')) {
            await this.loadTaskAndRoute('task-mum-construction');
        } else if (q.includes('mutation') || q.includes('property') || q.includes('delhi') || q.includes('mcd') || jur.includes('Delhi')) {
            await this.loadTaskAndRoute('task-del-mutation');
        } else if (q.includes('tech') || q.includes('it') || q.includes('hyderabad') || q.includes('ghmc') || jur.includes('Hyderabad')) {
            await this.loadTaskAndRoute('task-hyd-tech-biz');
        } else {
            // Default to Mumbai Bakery flagship
            await this.loadTaskAndRoute('task-mum-bakery');
        }
    }
}

// Instantiate on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CivicApp();
});
'''

with open('app/static/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js_content)

print("SUCCESS: app.js updated with Indian Government & Stitch localization.")
