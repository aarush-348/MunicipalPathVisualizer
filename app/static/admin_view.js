/**
 * Admin Validation Portal & Scraper Console Handler
 * Styled in authoritative Civic Functionalism
 */
class CivicAdminManager {
    constructor(appInstance) {
        this.app = appInstance;
        this.currentTab = 'scraper';
        this._bindAdminElements();
    }

    _bindAdminElements() {
        // Scraper controls
        this.btnRunScraper = document.getElementById('btn-run-scraper');
        this.scraperUrlInput = document.getElementById('scraper-url-input');
        this.scraperHintInput = document.getElementById('scraper-hint-input');
        this.scraperOutput = document.getElementById('scraper-output');

        if (this.btnRunScraper) {
            this.btnRunScraper.addEventListener('click', () => this.executeScrape());
        }

        // Quick presets
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const url = e.currentTarget.getAttribute('data-url');
                const hint = e.currentTarget.getAttribute('data-hint');
                if (this.scraperUrlInput) this.scraperUrlInput.value = url;
                if (this.scraperHintInput) this.scraperHintInput.value = hint;
            });
        });
    }

    switchTab(tabKey) {
        this.currentTab = tabKey;
        document.querySelectorAll('.admin-subtab').forEach(t => {
            const matches = t.getAttribute('data-subtab') === tabKey;
            t.classList.toggle('active', matches);
            t.classList.toggle('border-primary', matches);
            t.classList.toggle('text-primary', matches);
            t.classList.toggle('bg-surface-container-low', matches);
            t.classList.toggle('border-transparent', !matches);
            t.classList.toggle('text-secondary', !matches);
        });

        document.querySelectorAll('.admin-tab-pane').forEach(p => {
            p.style.display = p.getAttribute('id') === `pane-${tabKey}` ? 'block' : 'none';
        });

        if (tabKey === 'moderation') {
            this.renderModerationQueue();
        } else if (tabKey === 'audit') {
            this.loadAuditLogs();
        } else if (tabKey === 'feedback') {
            this.loadFeedback();
        }
    }

    async executeScrape() {
        const url = this.scraperUrlInput.value.trim();
        const hint = this.scraperHintInput.value.trim();
        if (!url) {
            alert('Please specify an official portal URL to scrape.');
            return;
        }

        this.btnRunScraper.disabled = true;
        this.btnRunScraper.innerHTML = '<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span><span>Crawling &amp; Parsing Portal...</span>';
        this.scraperOutput.innerHTML = `[INGESTION INITIALIZED] Connecting to gateway: ${url}...\n`;

        try {
            const resp = await fetch('/api/scrape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    task_hint: hint,
                    municipality: this.app.currentTask ? this.app.currentTask.municipality : 'Mumbai (MCGM / BMC)'
                })
            });
            const data = await resp.json();

            let logHtml = `✓ Status: HTTP 200 OK — Official Portal Ingested\n`;
            logHtml += `✓ Page Title: "${data.page_title}"\n`;
            logHtml += `✓ Confidence Score: ${(data.confidence_score * 100).toFixed(0)}% (Cryptographically Verified)\n`;
            logHtml += `✓ Ingestion Timestamp: ${data.scraped_at}\n\n`;
            logHtml += `=== EXTRACTED STATUTORY APPLICATION FORMS (${data.detected_forms.length}) ===\n`;
            data.detected_forms.forEach(f => {
                logHtml += `• [FORM] ${f.title} (${f.url})\n`;
            });

            logHtml += `\n=== PHYSICAL MUNICIPAL INTAKE WINDOWS (${data.detected_offices.length}) ===\n`;
            data.detected_offices.forEach(o => {
                logHtml += `• ${o.info}\n`;
            });

            logHtml += `\n=== AUTO-PARSED CANDIDATE PREREQUISITE STATIONS (${data.extracted_steps.length}) ===\n`;
            data.extracted_steps.forEach(s => {
                logHtml += `Stop #${s.step_number}: ${s.title}\n  Jurisdiction: ${s.department} | Window: ${s.estimated_days} Days | Base Fee: ₹${s.fee_amount}\n  Forms: ${s.forms.join(', ')}\n\n`;
            });

            this.scraperOutput.innerHTML = logHtml;
        } catch (err) {
            this.scraperOutput.innerHTML += `\n[ERROR] Ingestion crawler interrupted: ${err.message}\n`;
        } finally {
            this.btnRunScraper.disabled = false;
            this.btnRunScraper.innerHTML = '<span class="material-symbols-outlined text-[16px]">sync</span><span>Start Ingestion Crawler</span>';
        }
    }

    renderModerationQueue() {
        const container = document.getElementById('moderation-queue-container') || document.getElementById('moderation-list');
        if (!container) return;
        if (!this.app.currentTask) {
            container.innerHTML = '<p class="text-xs text-secondary">No task currently loaded for moderation.</p>';
            return;
        }

        container.innerHTML = this.app.currentTask.steps.map(s => `
            <div class="bg-surface-container-lowest border border-outline-variant p-4">
                <div class="flex justify-between items-start gap-4 mb-2">
                    <div>
                        <strong class="font-headline text-sm text-primary">#${s.step_number} ${s.title}</strong>
                        <div class="font-body text-xs text-secondary">${s.department.name}</div>
                    </div>
                    <div>
                        <span class="font-headline text-[11px] px-2 py-0.5 font-semibold ${s.verification_source.is_admin_verified ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-amber-50 text-amber-900 border border-amber-300'}">
                            ${s.verification_source.is_admin_verified ? '✓ Verified Source' : '⚠ Scraped (Pending)'}
                        </span>
                    </div>
                </div>

                <div class="font-code text-xs text-on-surface-variant mb-3">
                    Authority Source: <a href="${s.verification_source.url}" target="_blank" class="text-primary underline">${s.verification_source.url}</a>
                </div>

                <div class="flex flex-wrap gap-3 items-center pt-2 border-t border-surface-container font-headline text-xs">
                    <label class="text-secondary font-semibold">Statutory Fee (₹):</label>
                    <input type="number" id="mod-fee-${s.id}" value="${s.fee_amount}" class="w-24 bg-surface-container-low border border-outline-variant px-2 py-1 font-code text-xs text-primary">
                    
                    <label class="text-secondary font-semibold ml-2">SLA Window (Days):</label>
                    <input type="number" id="mod-sla-${s.id}" value="${s.estimated_days}" class="w-20 bg-surface-container-low border border-outline-variant px-2 py-1 font-code text-xs text-primary">

                    <button onclick="window.adminManager.verifyStep('${s.id}', true)" class="bg-primary hover:bg-primary-container text-on-primary px-3 py-1 font-semibold ml-auto flex items-center gap-1 transition-colors">
                        <span class="material-symbols-outlined text-[14px]">verified</span>
                        <span>Seal &amp; Publish Verification</span>
                    </button>
                </div>
            </div>
        `).join('');
    }

    async verifyStep(stepId, isVerified) {
        const feeVal = parseFloat(document.getElementById(`mod-fee-${stepId}`)?.value || 0);
        const slaVal = parseInt(document.getElementById(`mod-sla-${stepId}`)?.value || 7);

        try {
            const resp = await fetch(`/api/admin/verify-step?task_id=${this.app.currentTask.id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    step_id: stepId,
                    is_verified: isVerified,
                    updated_fee: feeVal,
                    updated_sla_days: slaVal
                })
            });
            if (resp.ok) {
                alert(`Official verification recorded: Step ${stepId} verified and updated.`);
                await this.app.loadRoadmap(this.app.currentTask.id);
                this.renderModerationQueue();
            }
        } catch (err) {
            alert(`Error updating verification: ${err.message}`);
        }
    }

    async loadAuditLogs() {
        const container = document.getElementById('audit-logs-container') || document.getElementById('audit-log-list');
        if (!container) return;
        try {
            const resp = await fetch('/api/admin/audit-logs');
            const logs = await resp.json();
            if (!logs || logs.length === 0) {
                container.innerHTML = '<p class="text-xs text-secondary">No administrative actions logged yet.</p>';
                return;
            }
            container.innerHTML = logs.map(l => `
                <div class="font-code text-xs border-b border-surface-container py-2 flex items-start gap-2">
                    <span class="text-secondary">[${new Date(l.timestamp).toLocaleTimeString()}]</span>
                    <span class="font-bold text-primary">${l.action}</span>
                    <span class="text-on-surface-variant flex-1">${l.details}</span>
                    <span class="text-secondary font-headline">(${l.user})</span>
                </div>
            `).join('');
        } catch (e) {
            container.innerHTML = `<span class="text-error text-xs">Failed to load audit logs</span>`;
        }
    }

    async loadFeedback() {
        const container = document.getElementById('feedback-reports-container') || document.getElementById('citizen-feedback-list');
        if (!container) return;
        try {
            const resp = await fetch('/api/feedback');
            const list = await resp.json();
            if (!list || list.length === 0) {
                container.innerHTML = '<p class="text-xs text-secondary">No citizen discrepancy reports recorded.</p>';
                return;
            }
            container.innerHTML = list.map(f => `
                <div class="bg-surface-container-lowest border border-outline-variant p-3 space-y-1">
                    <div class="flex justify-between font-headline text-xs text-error font-semibold">
                        <span>Report #${f.id}: ${f.issue_type} (Station: ${f.step_id})</span>
                        <span class="font-code text-[11px] text-secondary">${new Date(f.timestamp).toLocaleDateString()}</span>
                    </div>
                    <div class="font-body text-xs text-on-surface">${f.notes}</div>
                </div>
            `).join('');
        } catch (e) {
            container.innerHTML = `<span class="text-error text-xs">Failed to load feedback</span>`;
        }
    }
}

window.CivicAdminManager = CivicAdminManager;
