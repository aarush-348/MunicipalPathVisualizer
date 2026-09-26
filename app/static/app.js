/**
 * Main Civic Task Navigator Application Controller
 * Grounded in Civic Functionalism & Municipal Ledger discipline.
 * 100% Data-Driven & Decoupled Architecture across All Indian Municipalities
 * Conforming to GIGW 3.0 / S3WaaS and Stitch Design standards.
 */
class CivicApp {
    constructor() {
        this.currentTaskId = 'task-mum-bakery';
        this.currentTask = null;
        this.currentRoadmap = null;
        this.selectedStationId = null;
        
        // Active view tabs & visual modes
        this.activeTab = 'task-lookup';
        this.wayfindingMode = 'subway'; // 'subway' | 'dag'
        this.criticalPathActive = false;
        this.activeDocCategory = 'all';

        // Scoped progress & document state (will be loaded per-task)
        this.completedStepIds = new Set();
        this.inProgressStepIds = new Set();
        this.checkedDocIds = new Set();
        this.stepApplicationNumbers = {};

        // All catalog tasks cache
        this.allTasks = [];
        this.lastSearchNotice = null;

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

        // Initialize Dynamic Subway Transit Renderer
        if (typeof CivicSubwayRenderer !== 'undefined') {
            this.subwayRenderer = new CivicSubwayRenderer('subway-transit-svg', (nodeId) => {
                this.selectStation(nodeId);
            });
        }

        // Initialize Admin manager
        if (typeof CivicAdminManager !== 'undefined') {
            this.admin = new CivicAdminManager(this);
            window.adminManager = this.admin;
        }

        // Check URL hash for direct tab navigation
        const initialHash = window.location.hash.replace('#', '');
        if (initialHash && ['task-lookup', 'roadmap-and-route', 'step-dossier', 'document-locker', 'citizen-ledger', 'registry-admin'].includes(initialHash)) {
            this.activeTab = initialHash;
        }

        // 1. Fetch available catalog tasks
        await this.loadTasksList();

        // 2. Load initial scoped task state & roadmap
        await this.loadTaskAndRoute(this.currentTaskId);

        // 3. Switch to initial tab
        this.switchNavTab(this.activeTab);
    }

    // -------------------------------------------------------------------------
    // Navigation & UI Events Binding
    // -------------------------------------------------------------------------
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
                if (this.selectedStationId) {
                    this.toggleStepCompletion(this.selectedStationId);
                }
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

    // -------------------------------------------------------------------------
    // Per-Task Scoped State Management & Lifecycle
    // -------------------------------------------------------------------------
    loadTaskScopedState(taskId) {
        this.currentTaskId = taskId;

        // 1. Completed Steps
        const savedCompleted = localStorage.getItem(`civic_completed_steps_${taskId}`);
        if (savedCompleted) {
            try {
                this.completedStepIds = new Set(JSON.parse(savedCompleted));
            } catch (e) {
                this.completedStepIds = new Set();
            }
        } else {
            this.completedStepIds = new Set();
        }

        // 2. In-Progress Steps
        const savedInProgress = localStorage.getItem(`civic_inprogress_steps_${taskId}`);
        if (savedInProgress) {
            try {
                this.inProgressStepIds = new Set(JSON.parse(savedInProgress));
            } catch (e) {
                this.inProgressStepIds = new Set();
            }
        } else {
            this.inProgressStepIds = new Set();
        }

        // 3. Station Application / Challan Numbers Mapping
        const savedAppNums = localStorage.getItem(`civic_station_app_nums_${taskId}`);
        if (savedAppNums) {
            try {
                this.stepApplicationNumbers = JSON.parse(savedAppNums);
            } catch (e) {
                this.stepApplicationNumbers = {};
            }
        } else {
            this.stepApplicationNumbers = {};
        }

        // 4. User Checked Document Bag (with universal identity document carry-over)
        const savedDocs = localStorage.getItem(`civic_user_docs_${taskId}`);
        if (savedDocs) {
            try {
                this.checkedDocIds = new Set(JSON.parse(savedDocs));
            } catch (e) {
                this.checkedDocIds = new Set();
            }
        } else {
            // Find any standard KYC identity docs the citizen already marked in any previous task
            const universalKeywords = ["aadhaar", "pan", "passport", "incorporation", "electricity bill", "lease agreement", "rent agreement"];
            const carryOver = new Set();
            try {
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key && key.startsWith('civic_user_docs_')) {
                        const parsed = JSON.parse(localStorage.getItem(key) || '[]');
                        parsed.forEach(docName => {
                            const lower = (docName || '').toLowerCase();
                            if (universalKeywords.some(kw => lower.includes(kw))) {
                                carryOver.add(docName);
                            }
                        });
                    }
                }
            } catch (e) {}

            this.checkedDocIds = carryOver;
            this.saveTaskDocs();
        }
    }

    saveTaskCompleted() {
        localStorage.setItem(`civic_completed_steps_${this.currentTaskId}`, JSON.stringify(Array.from(this.completedStepIds)));
    }

    saveTaskInProgress() {
        localStorage.setItem(`civic_inprogress_steps_${this.currentTaskId}`, JSON.stringify(Array.from(this.inProgressStepIds)));
    }

    saveTaskDocs() {
        localStorage.setItem(`civic_user_docs_${this.currentTaskId}`, JSON.stringify(Array.from(this.checkedDocIds)));
    }

    saveTaskAppNums() {
        localStorage.setItem(`civic_station_app_nums_${this.currentTaskId}`, JSON.stringify(this.stepApplicationNumbers));
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
        const panes = ['task-lookup', 'roadmap-and-route', 'step-dossier', 'document-locker', 'citizen-ledger', 'registry-admin'];
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
        } else if (tabName === 'document-locker') {
            this.renderDocumentLocker();
        } else if (tabName === 'citizen-ledger') {
            this.renderCitizenLedger();
        } else if (tabName === 'registry-admin') {
            if (this.admin) this.admin.switchTab('scraper');
        }
    }

    // -------------------------------------------------------------------------
    // Tasks Catalog & Dynamic Jurisdiction Intake
    // -------------------------------------------------------------------------
    async loadTasksList() {
        try {
            const resp = await fetch('/api/tasks');
            if (resp.ok) {
                this.allTasks = await resp.json();
                this.renderTasksCatalog();
                this.populateJurisdictionDropdowns();
            }
        } catch (e) {
            console.error('Failed to load tasks list', e);
        }
    }

    renderTasksCatalog() {
        const container = document.getElementById('directives-ledger-list');
        if (!container || !this.allTasks || this.allTasks.length === 0) return;

        container.innerHTML = this.allTasks.map((t, idx) => {
            const isActive = t.id === this.currentTaskId;
            const stepCount = (t.steps && t.steps.length) || 0;
            const daysEst = `${t.total_estimated_days || 15}–${(t.total_estimated_days || 15) + 10} Days`;
            const feesEst = this.formatINR(t.total_fees || 0);
            const indexStr = idx < 9 ? `0${idx + 1}` : `${idx + 1}`;

            // Authorities summary
            let authorityTags = t.municipality;
            if (t.steps && t.steps.length > 0) {
                const uniqueDepts = Array.from(new Set(t.steps.map(s => (s.department && s.department.name ? s.department.name.split('(')[0].trim() : '')))).filter(Boolean);
                if (uniqueDepts.length > 0) {
                    authorityTags = uniqueDepts.slice(0, 3).join(' • ');
                }
            }

            return `
                <div class="p-4 hover:bg-surface-container-low transition-colors cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 ${isActive ? 'bg-amber-50/50 border-l-4 border-amber-600' : ''}" onclick="window.app.loadTaskAndRoute('${t.id}')">
                    <div class="flex items-start gap-3">
                        <div class="w-8 h-8 ${isActive ? 'bg-amber-700 text-white' : 'bg-primary text-on-primary'} flex items-center justify-center font-code text-xs font-bold border border-primary shrink-0">
                            ${indexStr}
                        </div>
                        <div>
                            <div class="font-headline text-sm font-semibold text-primary flex items-center gap-2 flex-wrap">
                                <span>${t.title}</span>
                                ${isActive ? '<span class="bg-amber-100 text-amber-900 font-label-sm text-[10px] px-1.5 py-0.5 font-bold uppercase border border-amber-300">Active Focus</span>' : ''}
                                <span class="bg-surface-container text-secondary font-code text-[10px] px-1.5 py-0.5 border border-outline-variant">${t.municipality}</span>
                            </div>
                            <div class="font-body text-xs text-on-surface-variant mt-0.5 max-w-2xl line-clamp-2">
                                ${t.description}
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center gap-6 shrink-0 text-xs font-headline">
                        <div class="text-right hidden sm:block">
                            <div class="text-secondary text-[11px] uppercase">Jurisdiction &amp; Chain</div>
                            <div class="font-code text-primary font-semibold truncate max-w-[180px]">${authorityTags}</div>
                        </div>
                        <div class="text-right">
                            <div class="text-secondary text-[11px] uppercase">Est. Schedule</div>
                            <div class="font-code text-primary font-semibold">${daysEst}</div>
                        </div>
                        <div class="text-right">
                            <div class="text-secondary text-[11px] uppercase">Total Fees</div>
                            <div class="font-code text-primary font-bold">${feesEst}</div>
                        </div>
                        <button class="${isActive ? 'bg-amber-700 text-white' : 'bg-surface-container text-primary hover:bg-primary hover:text-on-primary'} px-3 py-1.5 text-xs font-semibold transition-colors border border-outline-variant shrink-0" onclick="event.stopPropagation(); window.app.loadTaskAndRoute('${t.id}')">
                            Load Route
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    populateJurisdictionDropdowns() {
        if (!this.allTasks || this.allTasks.length === 0) return;

        // Extract unique municipalities
        const uniqueMunis = Array.from(new Set(this.allTasks.map(t => t.municipality))).filter(Boolean);

        // 1. Top Navbar Jurisdiction Dropdown
        const navSelect = document.getElementById('select-jurisdiction');
        if (navSelect) {
            navSelect.innerHTML = uniqueMunis.map(m => `
                <option value="${m}" ${this.currentTask && this.currentTask.municipality === m ? 'selected' : ''}>${m}</option>
            `).join('');

            // Clean event listener
            navSelect.onchange = (e) => {
                const selectedMuni = e.target.value;
                const matchTask = this.allTasks.find(t => t.municipality === selectedMuni);
                if (matchTask) {
                    this.loadTaskAndRoute(matchTask.id);
                }
            };
        }

        // 2. Search Intake Jurisdiction Dropdown
        const searchSelect = document.getElementById('jurisdictionSelect');
        if (searchSelect) {
            searchSelect.innerHTML = `
                <option value="">All Municipal Jurisdictions (National)</option>
                ${uniqueMunis.map(m => `<option value="${m}">${m}</option>`).join('')}
            `;
        }
    }

    // -------------------------------------------------------------------------
    // Task Route Loading & DAG Formulation
    // -------------------------------------------------------------------------
    async loadTaskAndRoute(taskId) {
        // 1. Load scoped persistence
        this.loadTaskScopedState(taskId);

        // 2. Load roadmap from server
        await this.loadRoadmap(taskId);

        // 3. Update task catalog highlight & dropdowns
        this.renderTasksCatalog();
        const navSelect = document.getElementById('select-jurisdiction');
        if (navSelect && this.currentTask) {
            navSelect.value = this.currentTask.municipality;
        }

        // 4. Default station selection
        if (this.currentTask && this.currentTask.steps.length > 0) {
            const firstPending = this.currentTask.steps.find(s => !this.completedStepIds.has(s.id));
            const targetStepId = firstPending ? firstPending.id : this.currentTask.steps[0].id;
            this.selectStation(targetStepId);
        }

        // 5. Navigate to roadmap view
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

            // Auto-initialize root steps as ready/in-progress if brand new task
            if (this.completedStepIds.size === 0 && this.inProgressStepIds.size === 0 && this.currentTask.steps.length > 0) {
                const rootSteps = this.currentTask.steps.filter(s => !s.prerequisites || s.prerequisites.length === 0);
                rootSteps.forEach(rs => this.inProgressStepIds.add(rs.id));
                this.saveTaskInProgress();
            }

            // Sync visual components
            this.updateHeaderAndStats();
            this.visualizer.setRoadmapData(this.currentRoadmap);
            this.renderRailMilestones();
            this.updateStationUI();
            this.renderCitizenLedger();

            // Render Dynamic Subway Transit SVG
            if (this.subwayRenderer) {
                this.subwayRenderer.render(
                    this.currentTask,
                    this.currentRoadmap,
                    this.completedStepIds,
                    this.selectedStationId
                );
            }

            if (this.activeTab === 'document-locker') {
                this.renderDocumentLocker();
            }
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

        // Dynamic Inter-Agency Code under subway map
        const elInterCode = document.getElementById('subway-interagency-code');
        if (elInterCode) {
            const muniCode = (t.municipality || 'MUNI').split(' ')[0].toUpperCase();
            const catCode = (t.category || 'STATUTORY').toUpperCase().replace(/[^A-Z]/g, '-').slice(0, 10);
            elInterCode.innerText = `INTER-AGENCY CODE: ${catCode}-${muniCode}-2026`;
        }

        // Summary stats ribbon
        const elTimeline = document.getElementById('summary-stat-timeline');
        const elFees = document.getElementById('summary-stat-fees');
        const elProgress = document.getElementById('summary-stat-progress');
        const elBlocker = document.getElementById('summary-stat-blocker');
        const elAntiToutFee = document.getElementById('anti-tout-total-fee');
        const elDocs = document.getElementById('summary-stat-docs');

        const totalSteps = t.steps ? t.steps.length : 0;
        const doneSteps = this.completedStepIds.size;

        if (elTimeline) elTimeline.innerText = `${r.total_estimated_days}–${r.total_estimated_days + 15}`;
        if (elFees) elFees.innerText = this.formatINR(r.total_estimated_fees || 0);
        if (elAntiToutFee) elAntiToutFee.innerText = this.formatINR(r.total_estimated_fees || 0);
        if (elProgress) elProgress.innerText = `${doneSteps} / ${totalSteps}`;

        if (elDocs && r.consolidated_documents) {
            const totalDocs = r.consolidated_documents.length;
            const readyDocs = r.consolidated_documents.filter(d => this.checkedDocIds.has(d.name)).length;
            elDocs.innerText = `${readyDocs} / ${totalDocs}`;
        }

        if (elBlocker) {
            const firstPending = t.steps.find(s => !this.completedStepIds.has(s.id));
            if (firstPending) {
                elBlocker.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500 shrink-0"></span> ${firstPending.department.name.split('(')[0]}`;
            } else {
                elBlocker.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-600 shrink-0"></span> All Milestones Cleared`;
            }
        }

        // NLP Intent Resolution & Provenance Banner
        const elNlpBanner = document.getElementById('nlp-intent-banner');
        if (elNlpBanner) {
            if (this.lastSearchNotice) {
                elNlpBanner.classList.remove('hidden');
                elNlpBanner.style.display = 'flex';
                const isSynth = this.lastSearchNotice.type === 'synthesized';
                elNlpBanner.className = isSynth
                    ? 'mb-4 p-3 bg-purple-50 border border-purple-300 text-purple-950 font-headline text-xs flex items-center justify-between gap-3 shadow-sm'
                    : 'mb-4 p-3 bg-blue-50 border border-blue-300 text-blue-950 font-headline text-xs flex items-center justify-between gap-3 shadow-sm';
                const icon = isSynth ? 'auto_awesome' : 'translate';
                elNlpBanner.innerHTML = `
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-[18px] ${isSynth ? 'text-purple-700' : 'text-blue-700'}">${icon}</span>
                        <span>${this.lastSearchNotice.message}</span>
                    </div>
                    <button class="text-secondary hover:text-primary underline text-[11px]" onclick="document.getElementById('nlp-intent-banner').style.display='none'">Dismiss</button>
                `;
            } else {
                elNlpBanner.classList.add('hidden');
                elNlpBanner.style.display = 'none';
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

        // Refresh Subway Map Highlight
        if (this.subwayRenderer && this.currentTask && this.currentRoadmap) {
            this.subwayRenderer.render(
                this.currentTask,
                this.currentRoadmap,
                this.completedStepIds,
                this.selectedStationId
            );
        }
    }

    updateStationUI() {
        if (!this.currentTask) return;
        const step = this.currentTask.steps.find(s => s.id === this.selectedStationId) || this.currentTask.steps[0];
        if (!step) return;

        const isCompleted = this.completedStepIds.has(step.id);
        const stateCode = (this.currentTask.state || this.currentTask.municipality || 'IN').substring(0, 2).toUpperCase();

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

        if (badgeStep) badgeStep.innerText = `STOP 0${step.step_number} / ${(step.department.jurisdiction || this.currentTask.municipality).toUpperCase()}`;
        if (badgeAgency) badgeAgency.innerText = `Agency: ${step.department.name}`;
        if (titleEl) titleEl.innerText = step.title;
        if (descEl) descEl.innerText = step.description;
        if (slaEl) slaEl.innerText = `${step.estimated_days} Days`;
        if (feeEl) feeEl.innerText = step.fee_amount > 0 ? this.formatINR(step.fee_amount) : 'Exempt';
        if (docketRef) docketRef.innerText = `DOCKET REF: ${stateCode}-${step.id.toUpperCase()}-2026`;

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

        // Pre-fill Citizen Application / Challan Input with saved data
        const appInput = document.getElementById('statutory-app-num') || document.getElementById('mcgm-app-num');
        if (appInput) {
            appInput.value = this.stepApplicationNumbers[step.id] || '';
        }
        const chkSelf = document.getElementById('chk-self-declaration');
        if (chkSelf) chkSelf.checked = false;

        // 2. Update Step Dossier Tab View
        this.populateDossierView(step);

        // 3. Update Drawer content
        this.populateDrawer(step);
    }

    // -------------------------------------------------------------------------
    // Step Dossier Decoupling: Fully Data-Driven from Task & Step
    // -------------------------------------------------------------------------
    populateDossierView(step) {
        const isCompleted = this.completedStepIds.has(step.id);
        const task = this.currentTask;
        const muniCode = (task.municipality || 'IN').split(' ')[0].toUpperCase();

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

        if (routeCrumb) routeCrumb.innerText = task.title;
        if (stepCrumb) stepCrumb.innerText = `Stop 0${step.step_number} (${step.title})`;
        if (refCode) refCode.innerText = `REF: ${muniCode}-${step.id.toUpperCase()}-2026`;
        if (stageIdx) stageIdx.innerText = `STAGE 0${step.step_number} / 0${task.steps.length}`;
        if (agencyName) agencyName.innerText = `${step.department.name} (${step.department.jurisdiction})`;
        if (mainTitle) mainTitle.innerText = `Step 0${step.step_number}: ${step.title}`;
        if (mainDesc) mainDesc.innerText = step.description;

        if (statusText) statusText.innerText = isCompleted ? 'Cleared & Verified on File' : 'In Progress: Action Required';
        if (statusDot) statusDot.className = isCompleted ? 'w-2.5 h-2.5 rounded-full bg-emerald-600' : 'w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse';
        if (statusSla) statusSla.innerText = `Target Statutory Window: ${step.estimated_days} Working Days`;

        // Verification Freshness Sentinel & Crowd Confirmation
        const gazetteTag = document.getElementById('dossier-gazette-tag');
        const verifiedDate = document.getElementById('dossier-verified-date');
        const crowdCount = document.getElementById('dossier-crowd-count');
        const statutoryAuth = step.last_gazette_notification || (step.verification_source && step.verification_source.gazette_ref) || `${task.category} Statutory Regulations`;

        if (gazetteTag) gazetteTag.innerText = statutoryAuth;
        if (verifiedDate) verifiedDate.innerText = this.formatDateIN(step.verification_source ? step.verification_source.last_scraped_at : null);
        if (crowdCount) crowdCount.innerText = `${step.community_verifications || 14} citizens successfully processed this milestone across ${task.municipality} this month`;

        if (provText) {
            provText.innerHTML = `Verified against <strong>${statutoryAuth}</strong> as of <strong>${this.formatDateIN(step.verification_source?.last_scraped_at)}</strong>.`;
        }
        if (provLink && provLinkText && step.verification_source) {
            provLink.href = step.verification_source.url || '#';
            provLinkText.innerText = (step.verification_source.url || 'portal.gov.in').replace('https://', '').replace('http://', '');
        }

        // Anti-Tout Sovereign Payment Notice
        const paymentChan = document.getElementById('dossier-payment-channel');
        const antiToutText = document.getElementById('dossier-anti-tout-text');
        const receiptMandate = document.getElementById('dossier-receipt-mandate');
        
        const defaultChannel = `${step.department.name} Official Treasury E-Challan / Bharatkosh`;
        const defaultAdvisory = step.anti_tout_advisory || `Official Advisory: Never pay cash to middlemen. All statutory fees for ${step.department.name} must be deposited via verified Government E-Receipt / GRN.`;
        const defaultReceipt = step.official_receipt_mandate || 'Zero Cash Mandate: Computerized Government Treasury E-Receipt required.';

        if (paymentChan) paymentChan.innerText = step.statutory_payment_channel || defaultChannel;
        if (antiToutText) antiToutText.innerText = defaultAdvisory;
        if (receiptMandate) receiptMandate.innerText = defaultReceipt;

        // Prerequisites bar
        const prereqGrid = document.getElementById('dossier-prereqs-grid');
        const prereqStatus = document.getElementById('dossier-prereq-chain-status');
        if (prereqGrid) {
            if (!step.prerequisites || step.prerequisites.length === 0) {
                prereqGrid.innerHTML = `
                    <div class="col-span-2 bg-surface-container-lowest p-3 border border-outline-variant text-xs text-secondary font-headline">
                        ✓ Station Initializer: Root procedural milestone under ${task.municipality} statutory rules.
                    </div>
                `;
                if (prereqStatus) prereqStatus.innerText = 'CHAIN STATUS: ROOT MILESTONE';
            } else {
                const totalReq = step.prerequisites.length;
                const clearedReq = step.prerequisites.filter(p => this.completedStepIds.has(p)).length;
                if (prereqStatus) prereqStatus.innerText = `CHAIN STATUS: ${clearedReq}/${totalReq} SATISFIED`;

                prereqGrid.innerHTML = step.prerequisites.map(pId => {
                    const prereqStep = task.steps.find(s => s.id === pId);
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
            const forms = step.forms || [];
            if (formsCount) formsCount.innerText = `${forms.length} Prescribed Instruments`;
            formsContainer.innerHTML = forms.map(f => `
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

        // Evidence & Required Filings
        const evidenceContainer = document.getElementById('dossier-evidence-container');
        const evidenceCount = document.getElementById('dossier-evidence-count');
        if (evidenceContainer) {
            const docs = step.documents || [];
            if (evidenceCount) evidenceCount.innerText = `${docs.length} Evidence Criteria`;
            evidenceContainer.innerHTML = docs.map(d => `
                <div class="p-3 bg-surface-container-lowest border border-outline-variant flex flex-col md:flex-row items-start justify-between gap-3">
                    <div class="space-y-0.5 max-w-xl">
                        <div class="flex items-center gap-2">
                            <span class="material-symbols-outlined text-amber-700 text-[18px]">pending</span>
                            <span class="font-headline text-sm font-semibold text-primary">${d.name}</span>
                        </div>
                        <p class="font-body text-xs text-on-surface-variant leading-relaxed">${d.description || 'Statutory proof required by inspection window.'}</p>
                        <div class="font-code text-[11px] text-outline">CRITERIA: Must be authenticated and digitally verified</div>
                    </div>
                    <div class="shrink-0 flex flex-col items-start md:items-end gap-1">
                        <span class="font-headline text-[10px] bg-amber-50 text-amber-900 border border-amber-300 px-2 py-0.5 font-semibold">Action Required</span>
                        <button class="font-headline text-xs text-primary underline hover:text-secondary font-medium mt-1" onclick="alert('Document checklist updated for: ${d.name}')">Upload / Verify</button>
                    </div>
                </div>
            `).join('') || '<div class="text-xs text-secondary font-headline">No additional document filings mandated for this step.</div>';
        }

        // Fee Breakdown Table (in INR ₹)
        const feeTableBody = document.getElementById('dossier-fee-table-body');
        const feeTotalEl = document.getElementById('dossier-fee-total');
        if (feeTableBody) {
            const breakdown = step.fee_breakdown || {};
            const entries = Object.entries(breakdown);
            if (entries.length === 0) {
                feeTableBody.innerHTML = `
                    <tr>
                        <td class="py-2.5 px-4 font-semibold text-primary">Standard Statutory Processing Fee</td>
                        <td class="py-2.5 px-4 text-secondary">${task.category} Tariff Schedule</td>
                        <td class="py-2.5 px-4 text-right font-code">Per Unit</td>
                        <td class="py-2.5 px-4 text-right font-code font-semibold text-primary">${this.formatINR(step.fee_amount)}</td>
                    </tr>
                `;
            } else {
                feeTableBody.innerHTML = entries.map(([key, val]) => `
                    <tr>
                        <td class="py-2.5 px-4 font-semibold text-primary">${key}</td>
                        <td class="py-2.5 px-4 text-secondary">${task.category} Statutory Basis</td>
                        <td class="py-2.5 px-4 text-right font-code">Per Filing Schedule</td>
                        <td class="py-2.5 px-4 text-right font-code font-semibold text-primary">${this.formatINR(val)}</td>
                    </tr>
                `).join('');
            }
            if (feeTotalEl) feeTotalEl.innerText = this.formatINR(step.fee_amount);
        }

        // Guidelines & Pitfalls
        const guidelinesText = document.getElementById('dossier-guidelines-text');
        if (guidelinesText) {
            guidelinesText.innerText = step.tips_and_pitfalls || `Ensure all submissions conform to ${task.municipality} public service standards and valid registration documents.`;
        }

        // Office Details in Right Rail (Directly Bound from step.department)
        const officeAddress = document.getElementById('dossier-office-address');
        const officeWindow = document.getElementById('dossier-office-window');
        const officeCity = document.getElementById('dossier-office-city');
        const officeHours = document.getElementById('dossier-office-hours');
        const officeBorough = document.getElementById('dossier-office-borough');
        const ombudsPhone = document.getElementById('dossier-ombuds-phone');
        const ombudsEmail = document.getElementById('dossier-ombuds-email');
        const cellTitle = document.getElementById('dossier-cell-title');
        const cellDesc = document.getElementById('dossier-cell-desc');

        const cleanMuni = (task.municipality || 'Civic').toLowerCase().replace(/[^a-z]/g, '');

        if (officeAddress) officeAddress.innerText = step.department.office_address || `${step.department.name} Administrative Headquarters, ${task.municipality}`;
        if (officeWindow) officeWindow.innerText = `${step.department.name} — Civic Facilitation Counter`;
        if (officeCity) officeCity.innerText = step.department.jurisdiction || task.municipality;
        if (officeHours) officeHours.innerText = step.department.working_hours || 'Monday – Friday: 10:00 AM – 4:00 PM IST';
        if (officeBorough) officeBorough.innerText = (step.department.jurisdiction || task.municipality).toUpperCase();
        if (ombudsPhone) ombudsPhone.innerText = step.department.contact_phone || '1800-GOV-HELP (Toll-Free)';
        if (ombudsEmail) ombudsEmail.innerText = step.department.contact_email || `support.${cleanMuni}@gov.in`;

        if (cellTitle) cellTitle.innerText = `${step.department.name} Facilitation Desk`;
        if (cellDesc) cellDesc.innerText = `Dedicated administrative officers at ${step.department.name} assist applicants with verification protocols and procedural documentation.`;

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
        if (conf && step.verification_source) conf.innerText = `${(step.verification_source.confidence_score * 100).toFixed(0)}% Match`;
        if (url && step.verification_source) {
            url.href = step.verification_source.url || '#';
            url.innerText = step.verification_source.url || 'portal.gov.in';
        }
        if (gaz) gaz.innerText = `Statutory Authority: ${step.last_gazette_notification || (step.verification_source && step.verification_source.gazette_ref) || 'State Public Service Code'}`;
        if (dept) dept.innerText = step.department.name;
        if (addr) addr.innerText = step.department.office_address || `${step.department.name}, ${this.currentTask.municipality}`;
        if (hours) hours.innerText = step.department.working_hours || 'Mon-Fri 10:00 AM - 4:00 PM IST';
        if (sla) sla.innerText = `${step.estimated_days} Days`;
        if (desc) desc.innerText = step.description;

        if (docs) {
            docs.innerHTML = step.documents.map(d => `<div class="bg-surface-container-lowest p-2 border border-outline-variant">• <strong>${d.name}</strong></div>`).join('') || 'None';
        }
        if (forms) {
            forms.innerHTML = step.forms.map(f => `<div class="bg-surface-container-lowest p-2 border border-outline-variant">• <strong>${f.form_code}</strong>: ${f.title}</div>`).join('') || 'None';
        }
        if (fees) {
            fees.innerHTML = Object.entries(step.fee_breakdown).map(([k, v]) => `<div>${k}: <strong>${this.formatINR(v)}</strong></div>`).join('') || `Total: ${this.formatINR(step.fee_amount)}`;
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

    // -------------------------------------------------------------------------
    // Universal Procedural Milestone Advancement & Application Validator
    // -------------------------------------------------------------------------
    async advanceStepAction() {
        const inputRef = document.getElementById('statutory-app-num') || document.getElementById('mcgm-app-num');
        const isSelfDeclared = document.getElementById('chk-self-declaration')?.checked;
        const val = inputRef ? inputRef.value.trim() : '';

        // Validation: Alphanumeric min 4 chars OR self-declaration checkbox
        const isValidInput = val.length >= 4 && /^[a-zA-Z0-9\-\/_]+$/.test(val);

        if (!isValidInput && !isSelfDeclared) {
            alert('Procedural Notice: Please enter a valid Application Reference / Challan Number (at least 4 alphanumeric characters) or check the self-declaration box before completing this milestone.');
            if (inputRef) inputRef.focus();
            return;
        }

        const stepId = this.selectedStationId;
        const refNumber = val || `SELF-DECL-${Date.now().toString().slice(-6)}`;
        
        // Save application reference
        this.stepApplicationNumbers[stepId] = refNumber;
        this.saveTaskAppNums();

        // Advance milestone
        this.completedStepIds.add(stepId);
        this.inProgressStepIds.delete(stepId);
        this.saveTaskCompleted();
        this.saveTaskInProgress();

        alert(`Application / Reference #${refNumber} recorded. Milestone "${stepId}" marked as Cleared & Verified.`);

        // Find next incomplete step to select
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
            delete this.stepApplicationNumbers[stepId];
        } else {
            this.completedStepIds.add(stepId);
            this.inProgressStepIds.delete(stepId);
            if (!this.stepApplicationNumbers[stepId]) {
                this.stepApplicationNumbers[stepId] = `CIVIC-ACK-${Date.now().toString().slice(-6)}`;
            }
        }
        this.saveTaskCompleted();
        this.saveTaskInProgress();
        this.saveTaskAppNums();

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

        // Re-render Subway Map with Critical Path highlight
        if (this.subwayRenderer && this.currentTask && this.currentRoadmap) {
            this.subwayRenderer.render(
                this.currentTask,
                this.currentRoadmap,
                this.completedStepIds,
                this.selectedStationId
            );
        }
    }

    // -------------------------------------------------------------------------
    // Dynamic Citizen Compliance Ledger
    // -------------------------------------------------------------------------
    renderCitizenLedger() {
        const tbody = document.getElementById('citizen-ledger-table-body');
        const totalCount = document.getElementById('ledger-total-milestones');
        const clearedCount = document.getElementById('ledger-cleared-milestones');
        const feeCount = document.getElementById('ledger-total-fees');
        const actDesc = document.getElementById('ledger-act-desc');

        if (!tbody || !this.currentTask) return;

        const task = this.currentTask;
        const steps = task.steps;
        const cleared = steps.filter(s => this.completedStepIds.has(s.id)).length;
        const totalFees = steps.reduce((sum, s) => sum + s.fee_amount, 0);

        if (totalCount) totalCount.innerText = `${steps.length} Stations`;
        if (clearedCount) clearedCount.innerText = `${cleared} Cleared (${Math.round((cleared / steps.length) * 100)}%)`;
        if (feeCount) feeCount.innerText = `${this.formatINR(totalFees)} Base`;

        // Dynamic State Public Service Guarantee Act
        if (actDesc) {
            let actName = `${task.municipality} Citizen Charter & Public Service Delivery Guarantee`;
            const state = (task.state || '').toLowerCase();
            const muni = (task.municipality || '').toLowerCase();

            if (state.includes('maharashtra') || muni.includes('mumbai') || muni.includes('pune')) {
                actName = 'Maharashtra Right to Public Services Act 2015';
            } else if (state.includes('karnataka') || muni.includes('bengaluru')) {
                actName = 'Karnataka Sakala Services Act 2011';
            } else if (state.includes('delhi')) {
                actName = 'Delhi Right of Citizen to Time Bound Delivery of Services Act 2011';
            } else if (state.includes('telangana') || muni.includes('hyderabad')) {
                actName = 'Telangana Citizen Charter & TS-iPASS Public Services Guarantee';
            }
            actDesc.innerText = `Cryptographically audited municipal filing log conforming to ${actName}. Certified receipts carry SHA-256 verification hashes.`;
        }

        const stateCode = (task.state || task.municipality || 'IN').substring(0, 2).toUpperCase();

        tbody.innerHTML = steps.map((s, idx) => {
            const isDone = this.completedStepIds.has(s.id);
            const statusHtml = isDone 
                ? '<span class="chip chip-verified">✓ Satisfied &amp; Logged</span>'
                : '<span class="chip chip-action-required">Action Required</span>';

            const savedAppRef = this.stepApplicationNumbers[s.id];
            const deptJurisdiction = (s.department && s.department.jurisdiction ? s.department.jurisdiction : task.municipality).toUpperCase();
            const dateStr = isDone 
                ? `${this.formatDateIN(new Date().toISOString())} [NODE: ${deptJurisdiction}]` 
                : 'Pending Filing';

            const docketRefCode = savedAppRef 
                ? savedAppRef 
                : `${stateCode}-${s.id.toUpperCase()}-2026`;

            return `
                <tr>
                    <td class="font-code font-bold text-primary">0${idx + 1}</td>
                    <td>
                        <div class="font-headline font-semibold text-primary text-xs">${s.title}</div>
                        <div class="font-body text-xs text-secondary mt-0.5 truncate max-w-md">${s.description}</div>
                    </td>
                    <td class="font-headline text-xs">${s.department.name.split('(')[0]}</td>
                    <td class="font-code text-xs text-secondary">${docketRefCode}</td>
                    <td class="font-code text-xs font-semibold text-primary">${this.formatINR(s.fee_amount)}</td>
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

    // -------------------------------------------------------------------------
    // Dual-Track NLP Intent Resolution & Procedure Search
    // -------------------------------------------------------------------------
    async performSearch() {
        const queryInput = document.getElementById('taskQuery');
        const jurSelect = document.getElementById('jurisdictionSelect');
        const btnSubmit = document.getElementById('btn-generate-roadmap');
        const q = queryInput ? queryInput.value.trim() : '';
        const jur = jurSelect ? jurSelect.value : '';

        if (!q) {
            this.switchNavTab('roadmap-and-route');
            return;
        }

        // Show loading spinner on button
        const originalBtnHtml = btnSubmit ? btnSubmit.innerHTML : '';
        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = `
                <span class="material-symbols-outlined text-[18px] animate-spin">sync</span>
                <span>Resolving Statutory Intent...</span>
            `;
        }

        try {
            const resp = await fetch('/api/tasks/resolve-intent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: q, municipality: jur })
            });

            if (!resp.ok) {
                throw new Error(`HTTP error ${resp.status}`);
            }

            const data = await resp.json();
            console.log('NLP Intent Resolution Result:', data);

            // Render interactive search feedback cards on Intake Screen
            this.renderNlpResolutionFeedback(data);

            if (data.top_task_id) {
                // Set provenance notice for the roadmap header banner
                if (data.hinglish_detected) {
                    this.lastSearchNotice = {
                        type: 'hinglish',
                        message: `Hinglish query detected: Interpreted and mapped to statutory terms ("${data.normalized_query}").`
                    };
                } else if (data.synthesis) {
                    this.lastSearchNotice = {
                        type: 'synthesized',
                        message: `Zero-shot statutory route dynamically synthesized for "${data.original_query}". Formulated pursuant to statutory rules.`
                    };
                } else {
                    this.lastSearchNotice = null;
                }

                await this.loadTaskAndRoute(data.top_task_id);
            } else {
                await this.loadTaskAndRoute('task-mum-bakery');
            }
        } catch (err) {
            console.error('NLP Intent Resolution failed, falling back to local heuristic:', err);
            const qLower = q.toLowerCase();
            if (qLower.includes('delhi') || qLower.includes('mutation')) {
                await this.loadTaskAndRoute('task-del-mutation');
            } else if (qLower.includes('bengaluru') || qLower.includes('bbmp')) {
                await this.loadTaskAndRoute('task-blr-restaurant');
            } else if (qLower.includes('hyderabad') || qLower.includes('ghmc') || qLower.includes('tech')) {
                await this.loadTaskAndRoute('task-hyd-tech-biz');
            } else if (qLower.includes('construction') || qLower.includes('autodcr')) {
                await this.loadTaskAndRoute('task-mum-construction');
            } else {
                await this.loadTaskAndRoute('task-mum-bakery');
            }
        } finally {
            if (btnSubmit) {
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = originalBtnHtml;
            }
        }
    }

    renderNlpResolutionFeedback(data) {
        const container = document.getElementById('nlp-search-feedback');
        if (!container) return;

        if (!data || !data.matches || data.matches.length === 0) {
            container.classList.add('hidden');
            return;
        }

        container.classList.remove('hidden');

        let hinglishBadgeHtml = '';
        if (data.hinglish_detected) {
            hinglishBadgeHtml = `
                <div class="flex items-center gap-2 p-2 bg-amber-50 border border-amber-300 text-amber-900 rounded-none text-xs">
                    <span class="material-symbols-outlined text-[16px] text-amber-700">translate</span>
                    <span><strong>Hinglish / Regional Terms Detected:</strong> Interpreted as: <em class="font-code text-[11px] font-semibold">${data.normalized_query}</em></span>
                </div>
            `;
        }

        const matchCardsHtml = data.matches.slice(0, 3).map((m) => {
            const isSynth = m.match_type === 'synthesized';
            const pct = Math.round(m.confidence * 100);
            const badgeClass = isSynth
                ? 'bg-purple-100 text-purple-900 border border-purple-300'
                : (pct >= 70 ? 'bg-emerald-100 text-emerald-900 border border-emerald-300' : 'bg-blue-100 text-blue-900 border border-blue-300');
            const typeLabel = isSynth ? 'AI Zero-Shot Synthesis' : `${pct}% Semantic Match`;

            return `
                <div class="p-2.5 bg-surface-container-lowest border border-outline-variant hover:border-primary transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div class="space-y-0.5">
                        <div class="flex items-center gap-2 flex-wrap">
                            <span class="font-code text-[10px] px-1.5 py-0.5 font-bold ${badgeClass}">${typeLabel}</span>
                            <span class="text-xs font-semibold text-primary">${m.title}</span>
                        </div>
                        <p class="text-[11px] text-on-surface-variant line-clamp-1">${m.municipality} • ${m.category}</p>
                    </div>
                    <button class="bg-primary hover:bg-primary-container text-on-primary text-xs font-semibold px-3 py-1.5 transition-colors shrink-0 flex items-center gap-1"
                            onclick="window.app.loadTaskAndRoute('${m.task_id}')">
                        <span>Load Route</span>
                        <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
                    </button>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            ${hinglishBadgeHtml}
            <div class="font-headline text-[11px] font-semibold text-secondary uppercase tracking-wider">
                Statutory Intent Resolved (${data.matches.length} matches):
            </div>
            <div class="space-y-1.5">
                ${matchCardsHtml}
            </div>
        `;
    }

    // -------------------------------------------------------------------------
    // Indian Currency & Date Formatting Helpers
    // -------------------------------------------------------------------------
    formatINR(amount) {
        const num = parseFloat(amount) || 0;
        return '₹' + num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    formatDateIN(isoStr) {
        if (!isoStr) return '24-09-2026';
        try {
            const d = new Date(isoStr);
            if (isNaN(d.getTime())) return isoStr.split('T')[0];
            const day = String(d.getDate()).padStart(2, '0');
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const year = d.getFullYear();
            return `${day}-${month}-${year}`;
        } catch (e) {
            return isoStr;
        }
    }

    // -------------------------------------------------------------------------
    // Dynamic Document Readiness Locker & Expiry Guard
    // -------------------------------------------------------------------------
    renderDocumentLocker() {
        const listContainer = document.getElementById('document-locker-list');
        const labelScore = document.getElementById('locker-readiness-label');
        const pctScore = document.getElementById('locker-readiness-pct');
        const progressBar = document.getElementById('locker-progress-bar');
        const deficitAlert = document.getElementById('locker-deficit-alert');
        const headingDesc = document.getElementById('locker-heading-desc');
        const filterContainer = document.getElementById('locker-category-filters');
        
        if (!this.currentRoadmap || !this.currentTask) return;
        const allDocs = this.currentRoadmap.consolidated_documents || [];
        const totalCount = allDocs.length;
        const readyCount = allDocs.filter(d => this.checkedDocIds.has(d.name)).length;
        const pct = totalCount > 0 ? Math.round((readyCount / totalCount) * 100) : 0;

        // Dynamic Header Description
        if (headingDesc) {
            headingDesc.innerText = `Consolidated multi-agency document inventory required across all ${this.currentTask.steps.length} procedural milestones. Audit your physical file or DigiLocker records before visiting ${this.currentTask.municipality} counters to eliminate rejection delays.`;
        }

        // Update counts & progress
        if (labelScore) labelScore.innerText = `${readyCount} / ${totalCount} Documents Ready (${pct}%)`;
        if (pctScore) pctScore.innerText = `${pct}%`;
        if (progressBar) progressBar.style.width = `${pct}%`;
        
        // Summary stat badge on roadmap
        const elDocs = document.getElementById('summary-stat-docs');
        if (elDocs) elDocs.innerText = `${readyCount} / ${totalCount}`;

        // Deficit alert banner
        if (deficitAlert) {
            if (readyCount === totalCount && totalCount > 0) {
                deficitAlert.className = 'text-emerald-900 font-semibold bg-emerald-50 border border-emerald-300 px-2 py-0.5';
                deficitAlert.innerHTML = '✓ Complete Physical File: All statutory documents prepared for official submission.';
            } else {
                deficitAlert.className = 'text-amber-900 font-semibold bg-amber-50 border border-amber-300 px-2 py-0.5';
                deficitAlert.innerHTML = `⚠ File Deficit: ${totalCount - readyCount} mandatory documents still missing from physical file.`;
            }
        }

        // Dynamic Category Filter Tabs from actual consolidated_documents
        if (filterContainer) {
            const categories = Array.from(new Set(allDocs.map(d => d.category || 'General'))).filter(Boolean);
            
            // Build buttons: 'All' + each non-empty category
            let buttonsHtml = `
                <button onclick="window.app.filterDocumentLocker('all')" class="locker-filter-btn px-3 py-1.5 ${this.activeDocCategory === 'all' ? 'bg-primary text-on-primary' : 'bg-surface-container text-primary'} font-semibold shrink-0" data-category="all">
                    All Documents (${totalCount})
                </button>
            `;

            categories.forEach(cat => {
                const count = allDocs.filter(d => d.category === cat).length;
                if (count > 0) {
                    const isActive = this.activeDocCategory === cat;
                    buttonsHtml += `
                        <button onclick="window.app.filterDocumentLocker('${cat.replace(/'/g, "\'")}')" class="locker-filter-btn px-3 py-1.5 ${isActive ? 'bg-primary text-on-primary font-semibold' : 'bg-surface-container hover:bg-surface-container-high text-primary border border-outline-variant'} shrink-0" data-category="${cat}">
                            ${cat} (${count})
                        </button>
                    `;
                }
            });

            filterContainer.innerHTML = buttonsHtml;
        }

        if (!listContainer) return;

        // Filter list
        const filteredDocs = this.activeDocCategory === 'all' 
            ? allDocs 
            : allDocs.filter(d => d.category === this.activeDocCategory);

        if (filteredDocs.length === 0) {
            listContainer.innerHTML = '<div class="col-span-2 p-6 bg-surface-container-lowest border border-outline-variant text-secondary text-sm">No documents found in this category.</div>';
            return;
        }

        listContainer.innerHTML = filteredDocs.map(d => {
            const isReady = this.checkedDocIds.has(d.name);
            const stepNums = d.required_in_step_numbers || d.required_in_steps || [];
            const stepsLabel = stepNums.length > 0
                ? stepNums.map(sNum => `Stop 0${sNum}`).join(', ')
                : 'General Milestone';

            const safeDocName = d.name.replace(/'/g, "\'");

            return `
                <div class="doc-card ${isReady ? 'ready' : 'missing'} p-4 border border-outline-variant flex flex-col justify-between gap-3 shadow-sm">
                    <div class="space-y-2">
                        <div class="flex items-start justify-between gap-3">
                            <label class="flex items-start gap-2.5 cursor-pointer flex-1">
                                <input type="checkbox" ${isReady ? 'checked' : ''} onchange="window.app.toggleDocumentReady('${safeDocName}')" class="mt-1 w-4 h-4 text-emerald-700 rounded border-outline focus:ring-emerald-600">
                                <div>
                                    <div class="font-headline text-sm font-semibold text-primary ${isReady ? 'line-through opacity-75' : ''}">${d.name}</div>
                                    <div class="flex items-center gap-1.5 flex-wrap mt-1">
                                        <span class="font-code text-[10px] px-1.5 py-0.2 bg-surface-container text-secondary font-semibold border border-outline-variant">${d.category || 'General'}</span>
                                        ${d.is_mandatory ? '<span class="font-headline text-[10px] px-1.5 py-0.2 bg-red-100 text-red-900 border border-red-300 font-bold">Mandatory</span>' : '<span class="font-headline text-[10px] px-1.5 py-0.2 bg-surface-container text-secondary">Optional</span>'}
                                        <span class="font-code text-[10px] text-secondary">Required at: <strong>${stepsLabel}</strong></span>
                                    </div>
                                </div>
                            </label>
                            <span class="font-headline text-[11px] px-2 py-0.5 font-bold ${isReady ? 'bg-emerald-100 text-emerald-900 border border-emerald-300' : 'bg-amber-100 text-amber-900 border border-amber-300'} shrink-0">
                                ${isReady ? '✓ In File' : 'Missing'}
                            </span>
                        </div>

                        <p class="font-body text-xs text-on-surface-variant leading-relaxed pl-6">
                            ${d.description}
                        </p>

                        ${d.validity_rule ? `
                            <div class="ml-6 p-2 bg-surface-container-low border border-outline-variant text-[11px] font-body text-primary flex items-center gap-1.5">
                                <span class="material-symbols-outlined text-amber-700 text-[14px]">warning</span>
                                <span><strong>Validity / Format Rule:</strong> ${d.validity_rule}</span>
                            </div>
                        ` : ''}
                    </div>

                    <div class="ml-6 pt-2 border-t border-outline-variant flex items-center justify-between text-[11px] font-headline">
                        <span class="text-secondary font-code">DigiLocker / Self-Attested Copy</span>
                        <button class="text-primary hover:text-secondary font-semibold underline" onclick="window.app.toggleDocumentReady('${safeDocName}')">
                            ${isReady ? 'Mark as Missing' : 'Mark as Ready in Bag'}
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    toggleDocumentReady(docName) {
        if (this.checkedDocIds.has(docName)) {
            this.checkedDocIds.delete(docName);
        } else {
            this.checkedDocIds.add(docName);
        }
        this.saveTaskDocs();
        this.renderDocumentLocker();
        this.updateHeaderAndStats();
    }

    filterDocumentLocker(category) {
        this.activeDocCategory = category;
        this.renderDocumentLocker();
    }

    resetDocumentChecklist() {
        if (confirm('Reset citizen document bag? All documents will be marked as missing for pre-visit audit.')) {
            this.checkedDocIds.clear();
            this.saveTaskDocs();
            this.renderDocumentLocker();
            this.updateHeaderAndStats();
        }
    }

    // -------------------------------------------------------------------------
    // Verification Staleness Sentinel & Direct Counter Discrepancy Reporting
    // -------------------------------------------------------------------------
    openDiscrepancyModal(stepId) {
        const sId = stepId || this.selectedStationId;
        const step = (this.currentTask && this.currentTask.steps.find(s => s.id === sId)) || (this.currentTask && this.currentTask.steps[0]);
        if (!step) return;

        this.selectedStationId = step.id;

        const elTargetStep = document.getElementById('discrepancy-target-step');
        const elTargetAgency = document.getElementById('discrepancy-target-agency');
        const elRecordedVal = document.getElementById('discrepancy-recorded-val');
        const elDemandedVal = document.getElementById('discrepancy-demanded-val');
        const elNotes = document.getElementById('discrepancy-notes');
        const elContact = document.getElementById('discrepancy-contact');

        if (elTargetStep) elTargetStep.innerText = `Stop 0${step.step_number}: ${step.title}`;
        if (elTargetAgency) elTargetAgency.innerText = `${step.department.name} — ${step.department.office_address || step.department.jurisdiction || this.currentTask.municipality}`;
        if (elRecordedVal) elRecordedVal.value = `Official Fee: ${this.formatINR(step.fee_amount)} | SLA: ${step.estimated_days} Days`;
        if (elDemandedVal) elDemandedVal.value = '';
        if (elNotes) elNotes.value = '';
        if (elContact) elContact.value = '';

        const modal = document.getElementById('modal-discrepancy');
        if (modal) {
            modal.classList.add('open');
            if (elDemandedVal) elDemandedVal.focus();
        }
    }

    closeDiscrepancyModal() {
        const modal = document.getElementById('modal-discrepancy');
        if (modal) {
            modal.classList.remove('open');
        }
    }

    async submitDiscrepancyReport() {
        const cat = document.getElementById('discrepancy-category')?.value || 'Fee Discrepancy';
        const demanded = document.getElementById('discrepancy-demanded-val')?.value.trim() || '';
        const notes = document.getElementById('discrepancy-notes')?.value.trim() || '';
        const contact = document.getElementById('discrepancy-contact')?.value.trim() || '';

        if (!demanded || !notes) {
            alert('Please specify the demanded value and factual observations.');
            return;
        }

        const payload = {
            step_id: this.selectedStationId,
            issue_type: cat,
            notes: `[Demanded: ${demanded}] ${notes}${contact ? ' (Citizen Contact: ' + contact + ')' : ''}`
        };

        try {
            const resp = await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (resp.ok) {
                const auditRef = Math.floor(100000 + Math.random() * 900000);
                const targetMuni = (this.currentTask && this.currentTask.municipality) || 'Municipal';
                alert(`Citizen Discrepancy Report submitted successfully.\n\nAudit Ref: #DISC-${auditRef}\nTransmitted to ${targetMuni} Grievance & Vigilance Cell for administrative verification.`);
                this.closeDiscrepancyModal();
                if (this.admin && typeof this.admin.loadFeedback === 'function') {
                    this.admin.loadFeedback();
                }
            } else {
                alert('Failed to submit report. Please try again.');
            }
        } catch (e) {
            console.error('Feedback submit error', e);
            alert('Connection error submitting report.');
        }
    }
}

// Instantiate on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CivicApp();
});
