# Python script to generate the fully India-localized index.html
# Conforms to Stitch Screens 1, 2, 3 and Indian Government GIGW 3.0 / S3WaaS standards

import os

html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  <meta content="web_standard" name="shell-type"/>
  <title>Civic Task Navigator | Municipal Route &amp; Compliance Directory (बृहन्मुंबई महानगरपालिका / MCGM &amp; Aaple Sarkar)</title>
  <meta name="description" content="Official Indian Municipal wayfinding directory and dependency graph resolver for civic tasks, statutory permits under MMC Act 1888, Shops Act, FSSAI, and multi-agency compliance."/>
  
  <!-- Fonts: IBM Plex Sans, Source Serif 4, JetBrains Mono, Material Symbols -->
  <link href="https://fonts.googleapis.com" rel="preconnect"/>
  <link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&amp;family=JetBrains+Mono:wght@400;500;600&amp;family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&amp;display=swap" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>

  <!-- Tailwind CSS Configuration matching Stitch Design Theme -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script id="tailwind-config">
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            "primary": "#000b21",
            "primary-container": "#152238",
            "on-primary": "#ffffff",
            "on-primary-container": "#7d89a4",
            "primary-fixed": "#d7e3ff",
            "primary-fixed-dim": "#bac7e4",
            "secondary": "#51606f",
            "secondary-container": "#d2e1f3",
            "on-secondary-container": "#556473",
            "tertiary": "#130a00",
            "tertiary-fixed": "#ffdeaa",
            "tertiary-fixed-dim": "#f5bd58",
            "background": "#f9faf8",
            "surface": "#f9faf8",
            "surface-dim": "#d9dad8",
            "surface-bright": "#f9faf8",
            "surface-container-lowest": "#ffffff",
            "surface-container-low": "#f3f4f2",
            "surface-container": "#edeeec",
            "surface-container-high": "#e7e8e6",
            "surface-container-highest": "#e2e3e1",
            "on-surface": "#191c1b",
            "on-surface-variant": "#44474d",
            "outline": "#75777e",
            "outline-variant": "#c5c6cd",
            "error": "#ba1a1a",
            "error-container": "#ffdad6",
            "on-error-container": "#93000a"
          },
          borderRadius: {
            DEFAULT: "0.25rem",
            sm: "0.125rem",
            md: "0.375rem",
            lg: "0.5rem"
          },
          fontFamily: {
            headline: ["'IBM Plex Sans'", "sans-serif"],
            body: ["'Source Serif 4'", "serif"],
            code: ["'JetBrains Mono'", "monospace"]
          }
        }
      }
    };
  </script>

  <!-- Custom Design System Stylesheet & GIGW Support -->
  <link rel="stylesheet" href="/static/style.css"/>
</head>

<body class="bg-background font-body text-on-surface antialiased min-h-screen flex flex-col" id="page-body">

  <!-- Accessibility: Skip to Main Content (GIGW Mandatory) -->
  <a href="#main-content" class="skip-link">मुख्य विषयवस्तु पर जाएं | Skip to main content</a>

  <!-- ======================================================================
       HEADER: National Tricolor Bar + Live Institutional Ticker + Main Nav
       ====================================================================== -->
  <header class="fixed top-0 left-0 right-0 w-full z-50 bg-surface-container-lowest border-b border-outline-variant">
    
    <!-- Indian National Tricolor Accent Strip -->
    <div class="gov-tricolor-strip">
      <div class="saffron"></div>
      <div class="white"></div>
      <div class="green"></div>
    </div>

    <!-- Top Live Ticker & GIGW Accessibility Bar -->
    <div class="bg-primary text-on-primary px-4 md:px-8 border-b border-primary-container">
      <div class="max-w-[1200px] mx-auto h-8 flex items-center justify-between text-[11px] font-headline font-semibold">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
            <span class="font-code text-primary-fixed">STATUS:</span>
            <span>Ledger Live &amp; Synchronized — MCGM Citizen Portal &amp; Aaple Sarkar Active</span>
          </div>
          <span class="text-outline-variant hidden sm:inline">|</span>
          <div class="hidden sm:flex items-center gap-2">
            <span class="text-primary-fixed-dim">FEED LATENCY:</span>
            <span class="font-code" id="ticker-latency">14ms</span>
          </div>
          <span class="text-outline-variant hidden lg:inline">|</span>
          <div class="hidden lg:flex items-center gap-1.5 text-primary-fixed-dim">
            <span class="font-code">NODE:</span>
            <span class="font-code text-primary-fixed">MUM-W-HW (BANDRA)</span>
          </div>
        </div>

        <!-- Right Side: GIGW Accessibility Tools & Controls -->
        <div class="flex items-center gap-3">
          <!-- Font Size Adjuster (A-, A, A+) -->
          <div class="flex items-center bg-primary-container border border-outline-variant/30 rounded px-1 text-[11px]">
            <button onclick="window.app.adjustFontSize('decrease')" class="px-1 text-primary-fixed-dim hover:text-on-primary" title="Decrease Font Size (A-)">A-</button>
            <span class="text-outline-variant/50">|</span>
            <button onclick="window.app.adjustFontSize('reset')" class="px-1 text-primary-fixed hover:text-on-primary font-bold" title="Reset Font Size (A)">A</button>
            <span class="text-outline-variant/50">|</span>
            <button onclick="window.app.adjustFontSize('increase')" class="px-1 text-primary-fixed-dim hover:text-on-primary" title="Increase Font Size (A+)">A+</button>
          </div>

          <!-- High Contrast Mode Toggle -->
          <button onclick="window.app.toggleHighContrast()" class="hidden md:flex items-center gap-1 text-[11px] bg-primary-container border border-outline-variant/30 px-2 py-0.5 rounded text-primary-fixed hover:text-on-primary" title="Toggle High Contrast Mode (कंट्रास्ट मोड)">
            <span class="material-symbols-outlined text-[13px]">contrast</span>
            <span>कंट्रास्ट</span>
          </button>

          <!-- Shortcuts -->
          <div class="hidden lg:flex items-center gap-2 text-primary-fixed-dim text-[11px]">
            <span class="font-code bg-primary-container px-1.5 py-0.5 border border-outline-variant/40 rounded">/</span>
            <span>Search</span>
            <span class="font-code bg-primary-container px-1.5 py-0.5 border border-outline-variant/40 rounded ml-1">ESC</span>
            <span>Close</span>
          </div>

          <!-- Emblem / Official Account Link -->
          <div class="w-5 h-5 rounded-full bg-primary-container border border-outline-variant/30 flex items-center justify-center cursor-pointer" title="Government of Maharashtra & MCGM Portal Authenticated">
            <span class="material-symbols-outlined text-primary-fixed text-[14px]">account_balance</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Navigation Bar -->
    <div class="h-20 bg-surface-container-lowest">
      <div class="max-w-[1200px] mx-auto h-20 px-4 md:px-8 flex items-center justify-between">
        
        <!-- Brand Insignia & Jurisdiction Selector -->
        <div class="flex items-center gap-5">
          <div class="flex items-center gap-3 pr-5 border-r border-outline-variant cursor-pointer" onclick="window.app.switchNavTab('task-lookup')">
            <div class="w-11 h-11 bg-primary text-on-primary flex items-center justify-center border border-primary">
              <span class="material-symbols-outlined text-[24px]">verified</span>
            </div>
            <div>
              <div class="font-headline text-sm font-bold text-primary uppercase tracking-tight flex items-center gap-1.5">
                <span>Civic Task Navigator</span>
                <span class="bg-amber-100 text-amber-900 border border-amber-300 font-code text-[10px] px-1 py-0.2 font-bold">INDIA</span>
              </div>
              <div class="font-headline text-[11px] text-secondary">
                Public Municipal Utility &amp; Docket System (नागरिक कार्य मार्गदर्शक)
              </div>
            </div>
          </div>

          <!-- Jurisdiction Selector -->
          <div class="hidden lg:flex flex-col">
            <span class="text-[10px] font-headline font-semibold text-outline uppercase tracking-wider">Jurisdiction (नगर निगम)</span>
            <div class="relative">
              <select id="select-jurisdiction" class="bg-transparent font-headline text-xs font-semibold text-primary focus:outline-none cursor-pointer pr-5 py-0.5">
                <option value="Mumbai" selected>Municipal Corporation of Greater Mumbai (MCGM / BMC)</option>
                <option value="Bengaluru">Bruhat Bengaluru Mahanagara Palike (BBMP)</option>
                <option value="Delhi">Municipal Corporation of Delhi (MCD / DORIS)</option>
                <option value="Hyderabad">Greater Hyderabad Municipal Corporation (GHMC / TS-bPASS)</option>
                <option value="Pune">Pune Municipal Corporation (PMC)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- 5 Top Primary Navigation Tabs -->
        <nav class="flex items-stretch h-full overflow-x-auto text-[13px] font-headline font-medium" id="top-nav-tabs">
          <a class="nav-tab-btn active" data-path="task-lookup" href="#task-lookup">
            <span>Task Lookup</span>
            <span class="text-[10px] opacity-75 ml-1 hidden xl:inline">/ कार्य खोज</span>
          </a>
          <a class="nav-tab-btn" data-path="roadmap-and-route" href="#roadmap-and-route">
            <span>Roadmap &amp; Route</span>
            <span class="text-[10px] opacity-75 ml-1 hidden xl:inline">/ प्रक्रिया मार्ग</span>
          </a>
          <a class="nav-tab-btn" data-path="step-dossier" href="#step-dossier">
            <span>Step Dossier</span>
            <span class="text-[10px] opacity-75 ml-1 hidden xl:inline">/ विस्तृत फाइल</span>
          </a>
          <a class="nav-tab-btn" data-path="citizen-ledger" href="#citizen-ledger">
            <span>Citizen Ledger</span>
            <span class="text-[10px] opacity-75 ml-1 hidden xl:inline">/ नागरिक खाता</span>
          </a>
          <a class="nav-tab-btn" data-path="registry-admin" href="#registry-admin">
            <span>Registry Admin</span>
            <span class="text-[10px] opacity-75 ml-1 hidden xl:inline">/ प्रशासन</span>
          </a>
        </nav>

        <!-- Right User / Audit Node Badge -->
        <div class="hidden sm:flex items-center gap-3 pl-4 border-l border-outline-variant">
          <button class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary hover:bg-primary-container transition-colors" title="Citizen Account / Docket Ledger" onclick="window.app.switchNavTab('citizen-ledger')">
            <span class="material-symbols-outlined text-[18px]">person</span>
          </button>
        </div>

      </div>
    </div>
  </header>

  <!-- ======================================================================
       MAIN CONTENT CONTAINER (5 TAB PANES)
       ====================================================================== -->
  <main class="flex-1 w-full pt-32 pb-16 bg-background" id="main-content">
    <div class="max-w-[1200px] mx-auto px-4 md:px-8">

      <!-- ==================================================================
           VIEW 1: TASK LOOKUP & MUNICIPAL INTAKE (Stitch Screen 1 Localized)
           ================================================================== -->
      <section id="view-task-lookup" class="tab-pane flex flex-col w-full">
        
        <!-- Official Municipal Protocol Banner -->
        <div class="bg-surface-container-high text-on-surface px-4 py-2.5 mb-6 flex flex-col md:flex-row md:items-center justify-between gap-2 shadow-sm rounded-none border-l-4 border-primary">
          <div class="flex items-center gap-2 text-xs font-headline font-semibold">
            <span class="bg-primary text-on-primary px-2 py-0.5 font-code tracking-wider uppercase text-[11px]">Docket Intake</span>
            <span class="text-sm uppercase tracking-tight text-primary">MCGM Ward H/West (Bandra West) — Aaple Sarkar Integrated Node</span>
          </div>
          <div class="flex items-center gap-4 font-code text-xs text-on-surface-variant">
            <span>NODE: <strong class="text-primary font-bold">MUM-W-HW</strong></span>
            <span>DISPATCH: <strong class="text-primary font-bold">AUTO-ROUTING ACTIVE</strong></span>
            <span class="bg-surface-container-lowest px-2 py-0.5 text-primary border border-outline-variant">MMC ACT § 394 COMPLIANT</span>
          </div>
        </div>

        <!-- Main Administrative Inquiry Deck (8 Cols Form / 4 Cols Preview) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-10">
          
          <!-- Left 8 Cols: Search & Parameter Form -->
          <div class="lg:col-span-8 flex flex-col">
            <div class="bg-surface-container-lowest p-6 shadow-sm border border-outline-variant flex flex-col justify-between h-full">
              <div>
                <!-- Header and Instruction -->
                <div class="mb-5">
                  <div class="font-headline text-[11px] font-semibold text-secondary uppercase tracking-widest mb-1">
                    Statutory Compliance Discovery Portal (महाराष्ट्र शासन व बीएमसी)
                  </div>
                  <h1 class="font-headline text-2xl md:text-3xl text-primary tracking-tight font-semibold mb-1">
                    Initiate Cross-Agency Procedure Route
                  </h1>
                  <p class="font-body text-sm text-on-surface-variant leading-relaxed">
                    Enter any municipal procedure, statutory trade license requirement, or commercial filing in Mumbai or across India to generate an ordered compliance route with rupee statutory fees, agency jurisdictions, and verified sequencing prerequisites.
                  </p>
                </div>

                <!-- Structured Form -->
                <form class="flex flex-col gap-4" id="taskIntakeForm" onsubmit="event.preventDefault(); window.app.performSearch();">
                  <div>
                    <label class="block font-headline text-xs font-semibold text-primary mb-1.5" for="taskQuery">
                      What civic or municipal procedure do you need to complete?
                    </label>
                    <div class="relative">
                      <input class="w-full bg-surface-container-lowest text-primary font-body text-base px-4 py-3 border border-outline focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent rounded-none" id="taskQuery" name="query" placeholder="e.g. Register &amp; Commission a Commercial Bakery in Bandra, Mumbai" type="text" value="Register &amp; Commission a Commercial Bakery in Bandra, Mumbai"/>
                      <button class="absolute right-3 top-3 text-secondary hover:text-primary" onclick="document.getElementById('taskQuery').value=''; document.getElementById('taskQuery').focus();" type="button" title="Clear search">
                        <span class="material-symbols-outlined text-[18px]">backspace</span>
                      </button>
                    </div>
                    <div class="mt-1.5 flex items-center justify-between text-xs">
                      <span class="font-body italic text-on-surface-variant text-xs">Natural language accepted. Keywords will cross-reference Mumbai Municipal Corporation Act (MMC Act 1888) &amp; Shops Act automatically.</span>
                      <span class="font-code text-[11px] text-secondary">SYNTAX: UTF-8 PLAIN</span>
                    </div>
                  </div>

                  <!-- Contextual Filters Grid -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                    <div class="bg-surface-container-low p-3 border border-outline-variant">
                      <label class="block font-headline text-[11px] font-semibold text-primary uppercase mb-1" for="jurisdictionSelect">
                        Target Municipal Jurisdiction
                      </label>
                      <div class="relative">
                        <select class="w-full bg-surface-container-lowest text-primary font-headline text-xs px-3 py-2 border border-outline-variant focus:outline-none focus:ring-1 focus:ring-primary appearance-none cursor-pointer" id="jurisdictionSelect">
                          <option value="Mumbai" selected>Greater Mumbai (BMC / Ward H/West, Bandra), Maharashtra</option>
                          <option value="Bengaluru">Bengaluru Urban (BBMP), Karnataka</option>
                          <option value="Delhi">National Capital Territory (MCD / DORIS), Delhi</option>
                          <option value="Hyderabad">Greater Hyderabad (GHMC / TS-bPASS), Telangana</option>
                          <option value="Pune">Pune Municipal Corporation (PMC), Maharashtra</option>
                        </select>
                        <span class="material-symbols-outlined absolute right-2.5 top-2.5 pointer-events-none text-secondary text-[18px]">unfold_more</span>
                      </div>
                    </div>

                    <div class="bg-surface-container-low p-3 border border-outline-variant">
                      <label class="block font-headline text-[11px] font-semibold text-primary uppercase mb-1" for="entityClassification">
                        Applicant / Entity Type
                      </label>
                      <div class="relative">
                        <select class="w-full bg-surface-container-lowest text-primary font-headline text-xs px-3 py-2 border border-outline-variant focus:outline-none focus:ring-1 focus:ring-primary appearance-none cursor-pointer" id="entityClassification">
                          <option value="commercial-pvt" selected>Commercial Enterprise (Pvt Ltd / LLP - SPICe+)</option>
                          <option value="sole-prop">Sole Proprietorship / Gumasta Intimation</option>
                          <option value="licensed-architect">MCGM Registered Architect / Licensed Surveyor</option>
                          <option value="chs">Cooperative Housing Society (CHS)</option>
                        </select>
                        <span class="material-symbols-outlined absolute right-2.5 top-2.5 pointer-events-none text-secondary text-[18px]">unfold_more</span>
                      </div>
                    </div>
                  </div>

                  <!-- Parameters Bar -->
                  <div class="bg-surface-container p-3 flex flex-wrap items-center justify-between gap-3 text-secondary font-headline text-xs border border-outline-variant">
                    <div class="flex items-center gap-2">
                      <span class="material-symbols-outlined text-[18px] text-primary">policy</span>
                      <span>Statutory Framework: <strong class="text-primary">MMC Act 1888 § 394 &amp; FoSCoS</strong></span>
                    </div>
                    <div class="flex items-center gap-4">
                      <label class="flex items-center gap-1.5 cursor-pointer text-primary">
                        <input checked="" class="w-4 h-4 text-primary rounded-none focus:ring-0 cursor-pointer" type="checkbox"/>
                        <span>Concurrent Department Clearance</span>
                      </label>
                      <label class="flex items-center gap-1.5 cursor-pointer text-primary">
                        <input checked="" class="w-4 h-4 text-primary rounded-none focus:ring-0 cursor-pointer" type="checkbox"/>
                        <span>Fee Challan Calculation (₹)</span>
                      </label>
                    </div>
                  </div>

                  <!-- Primary Action Bar -->
                  <div class="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <div class="flex items-center gap-1.5 text-on-surface-variant font-headline text-xs">
                      <span class="material-symbols-outlined text-[18px] text-amber-600">verified_user</span>
                      <span>Statutory Authority: Mumbai Municipal Corporation Act Section 394</span>
                    </div>
                    <button class="w-full sm:w-auto bg-primary text-on-primary px-6 py-3 font-headline text-sm font-semibold tracking-wide hover:bg-primary-container focus:outline-none focus:ring-2 focus:ring-primary transition-colors flex items-center justify-center gap-2 shadow-sm" type="submit" id="btn-generate-roadmap">
                      <span>Generate Compliance Roadmap</span>
                      <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- Right 4 Cols: Municipal Dispatch Summary & Live Feed (Stitch Screen 1) -->
          <div class="lg:col-span-4 flex flex-col gap-4">
            
            <!-- Active Filing Snapshot -->
            <div class="bg-surface-container-lowest p-4 shadow-sm border border-outline-variant">
              <div class="flex items-center justify-between pb-2 mb-3 bg-surface-container-low -mx-4 -mt-4 p-3 px-4 border-b border-outline-variant">
                <div class="font-headline text-xs font-semibold text-primary uppercase">Route Dispatch Preview</div>
                <span class="bg-primary text-on-primary font-code text-[11px] px-1.5 py-0.5 font-bold">EST. 45–65 DAYS</span>
              </div>
              <div class="space-y-2 text-xs font-headline">
                <div class="flex justify-between items-baseline py-1 border-b border-surface-container">
                  <span class="text-secondary">Direct Jurisdiction Count:</span>
                  <span class="font-code text-primary font-semibold">5 Authorities (MCGM, MFB, FSSAI, MPCB, MCA)</span>
                </div>
                <div class="flex justify-between items-baseline py-1 border-b border-surface-container">
                  <span class="text-secondary">Mandatory Sequence Steps:</span>
                  <span class="font-code text-primary font-semibold">8 Milestones (2 Concurrent Tracks)</span>
                </div>
                <div class="flex justify-between items-baseline py-1 border-b border-surface-container">
                  <span class="text-secondary">Statutory Municipal Fees:</span>
                  <span class="font-code text-primary font-semibold">₹52,400 Total Roadmap Base</span>
                </div>
                <div class="flex justify-between items-baseline py-1">
                  <span class="text-secondary">Active Stoppage / Blocker:</span>
                  <span class="bg-amber-100 text-amber-900 border border-amber-300 px-1.5 py-0.5 font-semibold text-[11px]">MFB Fire NOC Clearance</span>
                </div>
              </div>
              <div class="mt-4 pt-2 bg-surface-container p-2.5 border border-outline-variant">
                <div class="font-headline text-[11px] text-primary font-semibold uppercase mb-1.5">Mandatory Agency Sign-offs</div>
                <div class="flex flex-wrap gap-1 font-code text-[11px]">
                  <span class="bg-surface-container-lowest text-primary px-1.5 py-0.5 border border-outline-variant">MCGM Health (§ 394)</span>
                  <span class="bg-surface-container-lowest text-primary px-1.5 py-0.5 border border-outline-variant">Mumbai Fire Brigade (CFO)</span>
                  <span class="bg-surface-container-lowest text-primary px-1.5 py-0.5 border border-outline-variant">FSSAI FoSCoS</span>
                  <span class="bg-surface-container-lowest text-primary px-1.5 py-0.5 border border-outline-variant">MPCB Environment</span>
                  <span class="bg-surface-container-lowest text-primary px-1.5 py-0.5 border border-outline-variant">Aaple Sarkar</span>
                </div>
              </div>
            </div>

            <!-- Quick Registry Check Card -->
            <div class="bg-primary text-on-primary p-4 shadow-md flex-1 flex flex-col justify-between border border-primary-container">
              <div>
                <div class="flex items-center gap-1.5 font-headline text-xs text-primary-fixed mb-1 uppercase tracking-wider">
                  <span class="material-symbols-outlined text-[16px] text-amber-400">balance</span>
                  <span>Administrative Guarantee</span>
                </div>
                <h2 class="font-headline text-base text-on-primary font-semibold mb-1">Deterministic Statutory Sequencing</h2>
                <p class="font-body text-xs text-primary-fixed-dim leading-relaxed mb-3">
                  Routes generated by this terminal establish official administrative standing under the Maharashtra Right to Public Services Act 2015. Prescribed statutory timelines and prerequisites are verified against Municipal Corporation of Greater Mumbai regulations.
                </p>
              </div>
              <div class="pt-2 bg-primary-container p-2.5 flex items-center justify-between text-primary-fixed font-code text-xs border border-on-primary-container/30">
                <span>DOCKET ID REF:</span>
                <span class="text-on-primary font-bold">MCGM-HW-2024-842</span>
              </div>
            </div>

          </div>
        </div>

        <!-- Procedural Index Manifest: Pre-Compiled Municipal Master Directives -->
        <section class="mb-10">
          <div class="flex flex-col sm:flex-row sm:items-end justify-between mb-3">
            <div>
              <div class="font-headline text-[11px] font-semibold text-secondary uppercase tracking-widest">Procedural Index Manifest</div>
              <h2 class="font-headline text-xl text-primary font-semibold">Pre-Compiled Municipal Master Directives (प्रक्रिया निर्देशिका)</h2>
            </div>
            <div class="font-body text-xs text-secondary mt-1 sm:mt-0">
              Select a verified municipal route to load certified prerequisites and jurisdiction dependency trees.
            </div>
          </div>

          <!-- Official Ledger Grid List -->
          <div class="bg-surface-container-lowest shadow-sm border border-outline-variant divide-y divide-surface-container" id="directives-ledger-list">
            
            <!-- Item 1: Mumbai Commercial Bakery & Food Service Establishment (Flagship) -->
            <div class="p-4 hover:bg-surface-container-low transition-colors cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 bg-amber-50/40 border-l-4 border-amber-600" onclick="window.app.loadTaskAndRoute('task-mum-bakery')">
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-primary text-on-primary flex items-center justify-center font-code text-xs font-bold border border-primary">
                  01
                </div>
                <div>
                  <div class="font-headline text-sm font-semibold text-primary flex items-center gap-2">
                    <span>Register &amp; Commission a Commercial Bakery in Bandra, Mumbai</span>
                    <span class="bg-amber-100 text-amber-900 font-label-sm text-[10px] px-1.5 py-0.5 font-bold uppercase">Active Focus</span>
                  </div>
                  <div class="font-body text-xs text-on-surface-variant mt-0.5">
                    Statutory trade authorization under MMC Act 1888 § 394, MFB Fire Safety NOC, FoSCoS FSSAI State Food License, and MPCB pollution consent.
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-6 self-end md:self-center font-headline text-xs shrink-0">
                <div class="text-right">
                  <div class="text-secondary text-[11px] uppercase">JURISDICTIONS</div>
                  <div class="font-code text-primary font-semibold">MCGM • MFB • FSSAI • MPCB</div>
                </div>
                <div class="text-right">
                  <div class="text-secondary text-[11px] uppercase">EST. SCHEDULE</div>
                  <div class="font-code text-primary font-semibold">45–65 Days • ₹52,400</div>
                </div>
                <button class="bg-primary text-on-primary px-3 py-1 text-xs font-semibold hover:bg-primary-container transition-colors shadow-sm">
                  Load Route
                </button>
              </div>
            </div>

            <!-- Item 2: Mumbai Building Plan Sanction (AutoDCR) -->
            <div class="p-4 hover:bg-surface-container-low transition-colors cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4" onclick="window.app.loadTaskAndRoute('task-mum-construction')">
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-surface-container text-primary flex items-center justify-center font-code text-xs font-bold border border-outline-variant">
                  02
                </div>
                <div>
                  <div class="font-headline text-sm font-semibold text-primary">
                    Commercial Building Plan Sanction &amp; Occupancy Certificate (AutoDCR / BMC)
                  </div>
                  <div class="font-body text-xs text-on-surface-variant mt-0.5">
                    Architectural plan submission for commercial or residential modifications, tree authority NOC, fire brigade clearance, and municipal OC.
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-6 self-end md:self-center font-headline text-xs shrink-0">
                <div class="text-right">
                  <div class="text-secondary text-[11px] uppercase">JURISDICTIONS</div>
                  <div class="font-code text-primary font-semibold">BMC • FIRE BRIGADE</div>
                </div>
                <div class="text-right">
                  <div class="text-secondary text-[11px] uppercase">EST. SCHEDULE</div>
                  <div class="font-code text-primary font-semibold">55–90 Days</div>
                </div>
                <button class="bg-surface-container text-primary px-3 py-1 text-xs font-semibold hover:bg-primary hover:text-on-primary transition-colors border border-outline-variant">
                  Load Route
                </button>
              </div>
            </div>

            <!-- Item 3: Bengaluru BBMP Eating House -->
            <div class="p-4 hover:bg-surface-container-low transition-colors cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4" onclick="window.app.loadTaskAndRoute('task-blr-restaurant')">
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-surface-container text-primary flex items-center justify-center font-code text-xs font-bold border border-outline-variant">
                  03
                </div>
                <div>
                  <div class="font-headline text-sm font-semibold text-primary">
                    Open a Restaurant, Commercial Bakery or Cloud Kitchen (BBMP / FSSAI)
                  </div>
                  <div class="font-body text-xs text-on-surface-variant mt-0.5">
                    Statutory trade license issuance under Karnataka Municipalities Act, FSSAI FoSCoS food hygiene audit, and 60% Kannada signboard compliance.
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-6 self-end md:self-center font-headline text-xs shrink-0">
                <div class="text-right">
                  <div class="text-secondary text-[11px] uppercase">JURISDICTIONS</div>
                  <div class="font-code text-primary font-semibold">BBMP • FSSAI • KFES</div>
                </div>
                <div class="text-right">
                  <div class="text-secondary text-[11px] uppercase">EST. SCHEDULE</div>
                  <div class="font-code text-primary font-semibold">25–45 Days</div>
                </div>
                <button class="bg-surface-container text-primary px-3 py-1 text-xs font-semibold hover:bg-primary hover:text-on-primary transition-colors border border-outline-variant">
                  Load Route
                </button>
              </div>
            </div>

            <!-- Item 4: Delhi Property Tax Mutation -->
            <div class="p-4 hover:bg-surface-container-low transition-colors cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4" onclick="window.app.loadTaskAndRoute('task-del-mutation')">
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-surface-container text-primary flex items-center justify-center font-code text-xs font-bold border border-outline-variant">
                  04
                </div>
                <div>
                  <div class="font-headline text-sm font-semibold text-primary">
                    Property Tax Mutation &amp; Title Transfer (MCD / DORIS / GNCTD)
                  </div>
                  <div class="font-body text-xs text-on-surface-variant mt-0.5">
                    Statutory recording of property conveyance, No Dues Certificate generation, public notice objection period, and UPIC record update.
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-6 self-end md:self-center font-headline text-xs shrink-0">
                <div class="text-right">
                  <div class="text-secondary text-[11px] uppercase">JURISDICTIONS</div>
                  <div class="font-code text-primary font-semibold">MCD • DORIS REVENUE</div>
                </div>
                <div class="text-right">
                  <div class="text-secondary text-[11px] uppercase">EST. SCHEDULE</div>
                  <div class="font-code text-primary font-semibold">20–30 Days</div>
                </div>
                <button class="bg-surface-container text-primary px-3 py-1 text-xs font-semibold hover:bg-primary hover:text-on-primary transition-colors border border-outline-variant">
                  Load Route
                </button>
              </div>
            </div>

            <!-- Item 5: Hyderabad IT Office -->
            <div class="p-4 hover:bg-surface-container-low transition-colors cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4" onclick="window.app.loadTaskAndRoute('task-hyd-tech-biz')">
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-surface-container text-primary flex items-center justify-center font-code text-xs font-bold border border-outline-variant">
                  05
                </div>
                <div>
                  <div class="font-headline text-sm font-semibold text-primary">
                    Register an IT &amp; Tech Services Commercial Office (TS-bPASS / GHMC)
                  </div>
                  <div class="font-body text-xs text-on-surface-variant mt-0.5">
                    Rapid self-certification pathway under Telangana single-window system: instant trade license, labour registration, and Udyam MSME filing.
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-6 self-end md:self-center font-headline text-xs shrink-0">
                <div class="text-right">
                  <div class="text-secondary text-[11px] uppercase">JURISDICTIONS</div>
                  <div class="font-code text-primary font-semibold">GHMC • TS-bPASS</div>
                </div>
                <div class="text-right">
                  <div class="text-secondary text-[11px] uppercase">EST. SCHEDULE</div>
                  <div class="font-code text-primary font-semibold">5–7 Days</div>
                </div>
                <button class="bg-surface-container text-primary px-3 py-1 text-xs font-semibold hover:bg-primary hover:text-on-primary transition-colors border border-outline-variant">
                  Load Route
                </button>
              </div>
            </div>

          </div>
        </section>

        <!-- How the Navigator Reconciles Scattered Agency Rules (Civic Ledger System) -->
        <section class="mb-10">
          <div class="bg-surface-container-low p-6 border border-outline-variant">
            <div class="max-w-[760px] mb-5">
              <div class="font-headline text-[11px] font-semibold text-secondary uppercase tracking-widest mb-1">Procedural Architecture</div>
              <h2 class="font-headline text-xl text-primary font-semibold">How the Engine Reconciles Scattered Indian Municipal Mandates</h2>
              <p class="font-body text-xs text-on-surface-variant mt-1 leading-relaxed">
                Municipal administrative procedures traditionally stall when applicants submit filings out of order across Central, State, and Municipal departments. The Civic Task Navigator coordinates regulatory prerequisites into an immutable, step-by-step roadmap.
              </p>
            </div>
            <!-- 3-Column Structured Ledger Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <!-- Step 1 -->
              <div class="bg-surface-container-lowest p-4 border border-outline-variant flex flex-col justify-between">
                <div>
                  <div class="flex items-center justify-between pb-1 mb-2 bg-surface-container px-2 -mx-4 -mt-4 pt-2 border-b border-outline-variant">
                    <span class="font-code text-[11px] font-bold text-primary">01 / FEDERATION</span>
                    <span class="material-symbols-outlined text-[16px] text-secondary">input</span>
                  </div>
                  <h3 class="font-headline text-sm font-semibold text-primary mb-1">Department Feeds Ingestion</h3>
                  <p class="font-body text-xs text-on-surface-variant leading-relaxed">
                    Synchronizes real-time regulatory statutes, challan fee schedules, and required annexures across MCGM, Maharashtra Fire Services, FoSCoS (FSSAI), and MPCB.
                  </p>
                </div>
                <div class="mt-4 pt-2 bg-surface-container-low -mx-4 -mb-4 p-2.5 font-headline text-[11px] text-secondary border-t border-outline-variant">
                  <span>Sources:</span> <strong class="text-primary font-code">Aaple Sarkar, FoSCoS, MMC §394</strong>
                </div>
              </div>
              <!-- Step 2 -->
              <div class="bg-surface-container-lowest p-4 border border-outline-variant flex flex-col justify-between">
                <div>
                  <div class="flex items-center justify-between pb-1 mb-2 bg-surface-container px-2 -mx-4 -mt-4 pt-2 border-b border-outline-variant">
                    <span class="font-code text-[11px] font-bold text-primary">02 / SEQUENCING</span>
                    <span class="material-symbols-outlined text-[16px] text-secondary">account_tree</span>
                  </div>
                  <h3 class="font-headline text-sm font-semibold text-primary mb-1">Topological Dependency Sorting</h3>
                  <p class="font-body text-xs text-on-surface-variant leading-relaxed">
                    Constructs a directed acyclic graph to identify rigid procedural dependencies. For example, a BMC Health Trade License is mathematically locked until MFB Fire NOC and FSSAI clearances are satisfied.
                  </p>
                </div>
                <div class="mt-4 pt-2 bg-surface-container-low -mx-4 -mb-4 p-2.5 font-headline text-[11px] text-secondary border-t border-outline-variant">
                  <span>Algorithm:</span> <strong class="text-primary font-code">DAG Prerequisite Resolution</strong>
                </div>
              </div>
              <!-- Step 3 -->
              <div class="bg-surface-container-lowest p-4 border border-outline-variant flex flex-col justify-between">
                <div>
                  <div class="flex items-center justify-between pb-1 mb-2 bg-surface-container px-2 -mx-4 -mt-4 pt-2 border-b border-outline-variant">
                    <span class="font-code text-[11px] font-bold text-primary">03 / VERIFICATION</span>
                    <span class="material-symbols-outlined text-[16px] text-secondary">verified</span>
                  </div>
                  <h3 class="font-headline text-sm font-semibold text-primary mb-1">Direct Statutory Provenance</h3>
                  <p class="font-body text-xs text-on-surface-variant leading-relaxed">
                    Every challan fee line item, prescribed form, processing SLA window, and physical Ward CFC window links directly to the current governing gazette notification.
                  </p>
                </div>
                <div class="mt-4 pt-2 bg-surface-container-low -mx-4 -mb-4 p-2.5 font-headline text-[11px] text-secondary border-t border-outline-variant">
                  <span>Audit:</span> <strong class="text-primary font-code">SHA-256 Code Index Verified</strong>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Real-time Municipal Feed Status Bar -->
        <section class="bg-surface-container-lowest p-3 border border-outline-variant flex flex-wrap items-center justify-between gap-3 text-xs font-headline text-secondary">
          <div class="flex items-center gap-4 flex-wrap">
            <div class="flex items-center gap-1.5 text-primary font-semibold">
              <span class="w-2 h-2 rounded-full bg-emerald-600"></span>
              <span>REGISTRY INTEGRITY: <span class="font-code">99.8% VERIFIED</span></span>
            </div>
            <span class="text-outline-variant">|</span>
            <div class="flex items-center gap-1.5">
              <span class="font-code text-primary font-medium">MCGM PORTAL:</span>
              <span class="text-emerald-700 font-semibold">ACTIVE (EODB v4)</span>
            </div>
            <span class="text-outline-variant">|</span>
            <div class="flex items-center gap-1.5">
              <span class="font-code text-primary font-medium">AAPLE SARKAR:</span>
              <span class="text-primary font-semibold">GATEWAY SYNCHRONIZED</span>
            </div>
            <span class="text-outline-variant">|</span>
            <div class="flex items-center gap-1.5">
              <span class="font-code text-primary font-medium">FSSAI FoSCoS:</span>
              <span class="text-primary font-semibold">CENTRAL API CONNECTED</span>
            </div>
          </div>
          <div class="flex items-center gap-2 font-code text-on-surface-variant text-[11px]">
            <span>LATENCY: 14ms</span>
            <span>•</span>
            <span>CLUSTER: IN-WEST-MUM-01</span>
          </div>
        </section>

      </section>

      <!-- ==================================================================
           VIEW 2: ROADMAP VIEW — TRANSIT DEPENDENCY GRAPH (Stitch Screen 2 Localized)
           ================================================================== -->
      <section id="view-roadmap-and-route" class="tab-pane flex flex-col w-full" style="display:none;">
        
        <!-- Route Header & Administrative Metadata -->
        <div class="bg-surface-container-lowest p-6 border border-outline-variant shadow-sm mb-6">
          <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4 pb-4">
            <div class="space-y-1 max-w-3xl">
              <div class="flex items-center gap-2 flex-wrap text-xs">
                <span id="route-id-badge" class="bg-primary text-on-primary font-code px-2 py-0.5 rounded-none tracking-wide font-bold">ROUTE #MCGM-EODB-2024-8842</span>
                <span id="route-class-badge" class="bg-secondary-container text-on-secondary-container font-headline px-2 py-0.5 font-semibold uppercase">Commercial Eating House (Schedule M)</span>
                <span class="font-code text-secondary flex items-center gap-1 font-semibold">
                  <span class="w-2 h-2 rounded-full bg-emerald-600 inline-block"></span>
                  ACTIVE ROUTE MANIFEST
                </span>
              </div>
              <h1 id="roadmap-heading-title" class="font-headline text-2xl md:text-3xl text-primary font-semibold tracking-tight">
                Route Map: Commercial Bakery &amp; Cafe Bandra West (Ward H/West)
              </h1>
              <p id="roadmap-heading-desc" class="font-body text-sm text-on-surface-variant leading-relaxed">
                Municipal Corporation of Greater Mumbai (MCGM / BMC) — Public Health &amp; Fire Safety Regulatory Directory. Statutory pathway governing commercial bakery establishment with eating house authorization across MCGM, Mumbai Fire Brigade (MFB), FSSAI FoSCoS, and MPCB.
              </p>
            </div>

            <!-- Action Group -->
            <div class="flex items-center gap-2 flex-wrap">
              <!-- Switch between Subway Transit Map and Dynamic DAG Canvas -->
              <div class="flex bg-surface-container-low border border-outline-variant p-0.5">
                <button id="btn-mode-subway" class="px-3 py-1.5 font-headline text-xs font-semibold bg-primary text-on-primary" onclick="window.app.toggleWayfindingView('subway')">
                  Transit Spine Map
                </button>
                <button id="btn-mode-dag" class="px-3 py-1.5 font-headline text-xs font-semibold text-secondary hover:text-primary" onclick="window.app.toggleWayfindingView('dag')">
                  DAG Topology
                </button>
              </div>

              <button class="bg-surface-container-low hover:bg-surface-container text-primary font-headline text-xs px-3 py-2 border border-outline-variant flex items-center gap-1.5 transition-colors font-semibold" id="btn-toggle-critical" onclick="window.app.toggleCriticalPathHighlight()">
                <span class="material-symbols-outlined text-[16px]">alt_route</span>
                <span id="txt-critical">Show Critical Path Only</span>
              </button>
              
              <button class="bg-primary hover:bg-primary-container text-on-primary font-headline text-xs px-4 py-2 flex items-center gap-1.5 transition-colors shadow-sm font-semibold" onclick="window.print()">
                <span class="material-symbols-outlined text-[16px]">print</span>
                <span>Print Route Sheet</span>
              </button>
            </div>
          </div>

          <!-- Administrative Summary Ribbon -->
          <div class="bg-surface-container-low p-4 border border-outline-variant grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div class="space-y-0.5">
              <div class="font-headline text-[11px] text-secondary uppercase font-semibold">Total Estimated Timeline</div>
              <div class="font-headline text-xl text-primary font-bold flex items-baseline gap-1">
                <span id="summary-stat-timeline">45–65</span>
                <span class="font-headline text-xs text-secondary font-normal">Working Days</span>
              </div>
            </div>
            <div class="space-y-0.5">
              <div class="font-headline text-[11px] text-secondary uppercase font-semibold">Statutory Fees</div>
              <div class="font-headline text-xl text-primary font-bold flex items-baseline gap-1">
                <span id="summary-stat-fees">₹52,400.00</span>
                <span class="font-headline text-xs text-secondary font-normal">INR (₹)</span>
              </div>
            </div>
            <div class="space-y-0.5">
              <div class="font-headline text-[11px] text-secondary uppercase font-semibold">Station Progress</div>
              <div class="font-headline text-xl text-primary font-bold flex items-baseline gap-1">
                <span id="summary-stat-progress">2 / 8</span>
                <span class="font-headline text-xs text-secondary font-normal">Milestones Cleared</span>
              </div>
            </div>
            <div class="space-y-0.5">
              <div class="font-headline text-[11px] text-secondary uppercase font-semibold">Current Stoppage / Blocker</div>
              <div class="font-headline text-xs text-primary font-semibold truncate flex items-center gap-1" id="summary-stat-blocker">
                <span class="w-2 h-2 rounded-full bg-amber-500 shrink-0"></span>
                MFB Fire NOC &amp; Exhaust Clearance
              </div>
            </div>
          </div>
        </div>

        <!-- Wayfinding Layout Area (9 Cols Canvas / 3 Cols Cards) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-10">
          
          <!-- 9 Columns Wayfinding Board -->
          <div class="lg:col-span-9 flex flex-col space-y-4">
            
            <!-- TRANSIT SUBWAY MAP CONTAINER (Stitch Screen 2 Localized Precision) -->
            <div id="subway-diagram-wrapper" class="bg-surface-container-lowest p-6 border border-outline-variant shadow-sm overflow-x-auto relative">
              <div class="flex items-center justify-between pb-3 mb-2 border-b border-outline-variant">
                <div class="flex items-center gap-3">
                  <div class="font-headline text-xs font-bold tracking-wider text-primary uppercase flex items-center gap-1.5">
                    <span class="material-symbols-outlined text-[18px]">hub</span>
                    <span>Inter-Agency Transit Spine (Mumbai Municipal Network)</span>
                  </div>
                  <div class="hidden sm:flex items-center gap-3 font-code text-[11px] text-secondary">
                    <span class="inline-flex items-center gap-1"><span class="w-3 h-1 bg-emerald-700 inline-block"></span>Cleared Segment</span>
                    <span class="inline-flex items-center gap-1"><span class="w-3 h-1 bg-amber-500 inline-block"></span>Active Interchange</span>
                    <span class="inline-flex items-center gap-1"><span class="w-3 h-1 bg-slate-400 inline-block"></span>Upcoming Trunk</span>
                  </div>
                </div>
                <div class="font-code text-[11px] text-outline">SCALE: 1 STOP = 1 PREREQUISITE STAGE</div>
              </div>

              <!-- True Subway Transit SVG Diagram matching Stitch Screen 2 -->
              <div class="min-w-[860px] py-4 relative select-none">
                <svg class="w-full h-auto text-primary" viewBox="0 0 940 380" xmlns="http://www.w3.org/2000/svg" id="subway-transit-svg">
                  <!-- Background structural grid marks -->
                  <g stroke="#e2e3e1" stroke-dasharray="2,6" stroke-width="1">
                    <line x1="80" x2="80" y1="20" y2="360"></line>
                    <line x1="220" x2="220" y1="20" y2="360"></line>
                    <line x1="380" x2="380" y1="20" y2="360"></line>
                    <line x1="530" x2="530" y1="20" y2="360"></line>
                    <line x1="680" x2="680" y1="20" y2="360"></line>
                    <line x1="860" x2="860" y1="20" y2="360"></line>
                  </g>

                  <!-- 1. COMPLETED MAIN TRUNK: Stop 1 -> Stop 2 -> Stop 3 (Navy Casing with Green Core) -->
                  <path d="M 80 180 L 380 180" fill="none" stroke="#152238" stroke-linecap="round" stroke-width="12"></path>
                  <path d="M 80 180 L 380 180" fill="none" stroke="#2F6848" stroke-linecap="round" stroke-width="6" id="track-completed-trunk"></path>

                  <!-- 2. ACTIVE / BRANCH FORK: Stop 3 Splits to 3A and 3B Concurrent Paths -->
                  <!-- Branch 3A (Upward to FSSAI) -->
                  <path d="M 380 180 C 430 180, 450 90, 530 90" fill="none" id="branch-3a-casing" stroke="#152238" stroke-width="10"></path>
                  <path d="M 380 180 C 430 180, 450 90, 530 90" fill="none" id="branch-3a-line" stroke="#D9A441" stroke-dasharray="6,4" stroke-width="4"></path>

                  <!-- Branch 3B (Downward to MPCB) -->
                  <path d="M 380 180 C 430 180, 450 270, 530 270" fill="none" id="branch-3b-casing" stroke="#152238" stroke-width="10"></path>
                  <path d="M 380 180 C 430 180, 450 270, 530 270" fill="none" id="branch-3b-line" stroke="#D9A441" stroke-dasharray="6,4" stroke-width="4"></path>

                  <!-- Convergence Tracks into Stop 4 (BMC Section 394 Health Trade License) -->
                  <path d="M 530 90 C 610 90, 620 180, 680 180" fill="none" id="converge-3a-casing" stroke="#152238" stroke-width="10"></path>
                  <path d="M 530 90 C 610 90, 620 180, 680 180" fill="none" id="converge-3a-line" stroke="#94A3B8" stroke-width="4"></path>

                  <path d="M 530 270 C 610 270, 620 180, 680 180" fill="none" id="converge-3b-casing" stroke="#152238" stroke-width="10"></path>
                  <path d="M 530 270 C 610 270, 620 180, 680 180" fill="none" id="converge-3b-line" stroke="#94A3B8" stroke-width="4"></path>

                  <!-- 3. REMAINING UPCOMING TRUNK: Stop 4 -> Stop 5 -> Stop 6 -->
                  <path d="M 680 180 L 860 180" fill="none" stroke="#152238" stroke-linecap="round" stroke-width="12"></path>
                  <path d="M 680 180 L 860 180" fill="none" stroke="#CBD5E1" stroke-linecap="round" stroke-width="6" id="track-upcoming-trunk"></path>

                  <!-- TRACK LABELS -->
                  <text fill="#51606f" font-family="'JetBrains Mono'" font-size="10" font-weight="600" x="300" y="162">MAIN TRUNK LINE</text>
                  <text fill="#D9A441" font-family="'JetBrains Mono'" font-size="10" font-weight="600" x="420" y="70">TRANSFER BRANCH 3A [FSSAI]</text>
                  <text fill="#D9A441" font-family="'JetBrains Mono'" font-size="10" font-weight="600" x="420" y="300">TRANSFER BRANCH 3B [MPCB]</text>
                  <text fill="#75777e" font-family="'JetBrains Mono'" font-size="10" font-weight="600" x="720" y="162">FINAL CLEARANCE TRACK</text>

                  <!-- STATIONS / STOP NODES -->
                  <!-- STOP 01: MCA COI & PAN (Completed) -->
                  <g class="cursor-pointer group" onclick="window.app.selectStation('mum-bakery-1')">
                    <circle cx="80" cy="180" fill="#152238" r="16"></circle>
                    <circle cx="80" cy="180" fill="#2F6848" r="12"></circle>
                    <path d="M 74 180 L 78 184 L 86 175" fill="none" stroke="#FFFFFF" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"></path>
                    <text fill="#152238" font-family="'IBM Plex Sans'" font-size="12" font-weight="600" text-anchor="middle" x="80" y="215">01. MCA COI &amp; PAN</text>
                    <text fill="#2F6848" font-family="'JetBrains Mono'" font-size="10" text-anchor="middle" x="80" y="230">CLEARED 12 AUG</text>
                  </g>

                  <!-- STOP 02: Commercial Lease & Gumasta (Completed) -->
                  <g class="cursor-pointer group" onclick="window.app.selectStation('mum-bakery-2')">
                    <circle cx="220" cy="180" fill="#152238" r="16"></circle>
                    <circle cx="220" cy="180" fill="#2F6848" r="12"></circle>
                    <path d="M 214 180 L 218 184 L 226 175" fill="none" stroke="#FFFFFF" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"></path>
                    <text fill="#152238" font-family="'IBM Plex Sans'" font-size="12" font-weight="600" text-anchor="middle" x="220" y="215">02. LEASE &amp; GUMASTA</text>
                    <text fill="#2F6848" font-family="'JetBrains Mono'" font-size="10" text-anchor="middle" x="220" y="230">CLEARED 28 AUG</text>
                  </g>

                  <!-- STOP 03: MFB Fire Safety NOC & Kitchen Exhaust (ACTIVE INTERCHANGE) -->
                  <g class="cursor-pointer group" onclick="window.app.selectStation('mum-bakery-3')">
                    <circle class="animate-pulse" cx="380" cy="180" fill="#D9A441" fill-opacity="0.3" r="24"></circle>
                    <circle cx="380" cy="180" fill="#152238" r="18"></circle>
                    <circle cx="380" cy="180" fill="#FFFFFF" r="13"></circle>
                    <circle cx="380" cy="180" fill="#D9A441" r="8"></circle>
                    <text fill="#152238" font-family="'IBM Plex Sans'" font-size="13" font-weight="700" text-anchor="middle" x="380" y="145">03. MFB FIRE NOC &amp; EXHAUST</text>
                    <text fill="#8A5800" font-family="'JetBrains Mono'" font-size="10" font-weight="600" text-anchor="middle" x="380" y="130">IN PROGRESS (ACTIVE)</text>
                    <rect fill="#FDF3E7" height="18" rx="2" stroke="#D9A441" stroke-width="1" width="68" x="346" y="206"></rect>
                    <text fill="#8A5800" font-family="'JetBrains Mono'" font-size="10" font-weight="600" text-anchor="middle" x="380" y="219">15-21 DAYS</text>
                  </g>

                  <!-- STOP 03A: FSSAI State License (Parallel Branch) -->
                  <g class="cursor-pointer group" id="node-3a" onclick="window.app.selectStation('mum-bakery-3a')">
                    <rect fill="#152238" height="32" rx="4" width="32" x="514" y="74"></rect>
                    <rect fill="#FFFFFF" height="26" rx="2" width="26" x="517" y="77"></rect>
                    <circle cx="530" cy="90" fill="#D9A441" r="6"></circle>
                    <text fill="#152238" font-family="'IBM Plex Sans'" font-size="12" font-weight="600" text-anchor="middle" x="530" y="55">03A. FSSAI STATE LICENSE</text>
                    <text fill="#51606f" font-family="'JetBrains Mono'" font-size="9" text-anchor="middle" x="530" y="122">CONCURRENT TRACK</text>
                  </g>

                  <!-- STOP 03B: MPCB Pollution Consent (Parallel Branch) -->
                  <g class="cursor-pointer group" id="node-3b" onclick="window.app.selectStation('mum-bakery-3b')">
                    <rect fill="#152238" height="32" rx="4" width="32" x="514" y="254"></rect>
                    <rect fill="#FFFFFF" height="26" rx="2" width="26" x="517" y="257"></rect>
                    <circle cx="530" cy="270" fill="#D9A441" r="6"></circle>
                    <text fill="#152238" font-family="'IBM Plex Sans'" font-size="12" font-weight="600" text-anchor="middle" x="530" y="305">03B. MPCB POLLUTION</text>
                    <text fill="#51606f" font-family="'JetBrains Mono'" font-size="9" text-anchor="middle" x="530" y="320">CONCURRENT TRACK</text>
                  </g>

                  <!-- STOP 04: BMC Section 394 Health Trade License (Upcoming Convergence) -->
                  <g class="cursor-pointer group" onclick="window.app.selectStation('mum-bakery-4')">
                    <circle cx="680" cy="180" fill="#152238" r="16"></circle>
                    <circle cx="680" cy="180" fill="#FFFFFF" r="12"></circle>
                    <circle cx="680" cy="180" fill="#5C6B7A" r="6"></circle>
                    <text fill="#152238" font-family="'IBM Plex Sans'" font-size="12" font-weight="600" text-anchor="middle" x="680" y="215">04. BMC HEALTH LICENSE (§394)</text>
                    <text fill="#75777e" font-family="'JetBrains Mono'" font-size="10" text-anchor="middle" x="680" y="230">LOCKED (PENDING FIRE NOC)</text>
                  </g>

                  <!-- STOP 05: Facade Signboard & Police NOC -->
                  <g class="cursor-pointer group" onclick="window.app.selectStation('mum-bakery-5')">
                    <circle cx="780" cy="180" fill="#152238" r="14"></circle>
                    <circle cx="780" cy="180" fill="#FFFFFF" r="10"></circle>
                    <circle cx="780" cy="180" fill="#5C6B7A" r="5"></circle>
                    <text fill="#152238" font-family="'IBM Plex Sans'" font-size="11" font-weight="600" text-anchor="middle" x="780" y="150">05. SIGNBOARD &amp; POLICE NOC</text>
                    <text fill="#75777e" font-family="'JetBrains Mono'" font-size="9" text-anchor="middle" x="780" y="215">UPCOMING</text>
                  </g>

                  <!-- STOP 06: Final Health Trade Certificate & Official Seal (Terminus) -->
                  <g class="cursor-pointer group" onclick="window.app.selectStation('mum-bakery-6')">
                    <circle cx="860" cy="180" fill="#152238" r="18"></circle>
                    <circle cx="860" cy="180" fill="#FFFFFF" r="14"></circle>
                    <circle cx="860" cy="180" fill="#152238" r="10"></circle>
                    <circle cx="860" cy="180" fill="#D7E3FF" r="5"></circle>
                    <text fill="#152238" font-family="'IBM Plex Sans'" font-size="12" font-weight="700" text-anchor="middle" x="860" y="215">06. FINAL PERMIT &amp; SEAL</text>
                    <text fill="#152238" font-family="'JetBrains Mono'" font-size="10" text-anchor="middle" x="860" y="230">TERMINUS</text>
                  </g>
                </svg>
              </div>

              <div class="bg-surface-container-low px-4 py-2 border-t border-outline-variant text-xs text-on-surface-variant flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-[16px] text-primary">info</span>
                  <span>Click any transit station node or station stop card below to view detailed requirements and evidence records.</span>
                </div>
                <span class="font-code text-[11px] text-outline">INTER-AGENCY CODE: MMC-ACT-1888-MAHA</span>
              </div>
            </div>

            <!-- DYNAMIC DAG CANVAS WRAPPER (Alternative Interactive View) -->
            <div id="dag-canvas-wrapper" class="bg-surface-container-lowest p-4 border border-outline-variant shadow-sm relative" style="display:none; height: 500px;">
              <div class="canvas-toolbar">
                <button class="tool-btn" id="btn-zoom-in" title="Zoom In">+</button>
                <button class="tool-btn" id="btn-zoom-out" title="Zoom Out">-</button>
                <button class="tool-btn" id="btn-fit-screen" title="Fit to Screen">Fit</button>
                <button class="tool-btn" id="btn-reset-view" title="Reset View">Reset</button>
              </div>
              <svg id="graph-canvas" class="w-full h-full cursor-grab"></svg>
            </div>

            <!-- ACTIVE STATION DOSSIER & DETAILED STOP CARDS (Stitch Screen 2 Precision) -->
            <div class="space-y-4">
              <!-- CARD 03: THE ACTIVE FOCUS (Mumbai Fire Brigade Fire NOC & Kitchen Exhaust) -->
              <article class="bg-surface-container-lowest p-6 shadow-sm border-l-4 border-amber-500 border border-outline-variant relative" id="stop-03">
                <!-- Card Header / Provenance Bar -->
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 mb-4 border-b border-outline-variant">
                  <div class="flex items-center gap-2">
                    <span id="station-badge-step" class="bg-primary text-on-primary font-code text-xs px-2 py-0.5 rounded-none font-bold">STOP 03 / MAIN TRUNK</span>
                    <span id="station-badge-status" class="bg-amber-100 text-amber-900 font-headline text-xs px-2.5 py-0.5 rounded-none font-bold uppercase flex items-center gap-1">
                      <span class="w-2 h-2 rounded-full bg-amber-600 animate-ping"></span>
                      In Progress
                    </span>
                    <span id="station-badge-agency" class="bg-surface-container text-on-surface font-headline text-xs px-2 py-0.5 rounded-none font-medium">Agency: Mumbai Fire Brigade (Chief Fire Officer)</span>
                  </div>
                  <div id="station-docket-ref" class="font-code text-xs text-secondary">
                    DOCKET REF: MFB-NOC-2024-MUM-77192
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div class="md:col-span-2 space-y-2">
                    <h2 id="station-title" class="font-headline text-xl text-primary font-semibold">
                      Obtain MFB Fire Safety Compliance &amp; Commercial Kitchen NOC
                    </h2>
                    <p id="station-desc" class="font-body text-sm text-on-surface leading-relaxed">
                      Mandatory fire protection installation, Class-K commercial exhaust hood duct suppression, LPG pipeline safety valve certificate, and dual emergency escape audit pursuant to Maharashtra Fire Prevention and Life Safety Measures Act 2006.
                    </p>
                    
                    <!-- Prerequisite Checklist within active card -->
                    <div class="bg-surface-container-low p-4 rounded-none space-y-2 mt-3 border border-outline-variant">
                      <div class="font-headline text-xs uppercase font-semibold text-primary">Mandatory Evidence &amp; Filings Needed for Stop Clearance:</div>
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1" id="station-checklist">
                        <label class="flex items-start gap-1.5 font-body text-xs text-on-surface cursor-pointer">
                          <span class="material-symbols-outlined text-emerald-700 text-[18px]">check_box</span>
                          <span>Form A Application under Maharashtra Fire Act</span>
                        </label>
                        <label class="flex items-start gap-1.5 font-body text-xs text-on-surface cursor-pointer">
                          <span class="material-symbols-outlined text-emerald-700 text-[18px]">check_box</span>
                          <span>Registered Lease &amp; Gumasta Registration (From Stop 02)</span>
                        </label>
                        <label class="flex items-start gap-1.5 font-body text-xs text-on-surface cursor-pointer">
                          <span class="material-symbols-outlined text-amber-600 text-[18px]">indeterminate_check_box</span>
                          <span>Structural Layout with Exhaust Duct Routing (In Review)</span>
                        </label>
                        <label class="flex items-start gap-1.5 font-body text-xs text-on-surface cursor-pointer">
                          <span class="material-symbols-outlined text-outline text-[18px]">check_box_outline_blank</span>
                          <span>Licensed Fire Agency Form B &amp; Hydrant Certificate</span>
                        </label>
                      </div>
                    </div>
                  </div>

                  <!-- Stop Metrics Side Panel -->
                  <div class="bg-surface-container p-4 rounded-none flex flex-col justify-between space-y-4 border border-outline-variant">
                    <div class="space-y-1">
                      <div class="font-headline text-xs text-secondary uppercase font-semibold">Statutory Service Standards</div>
                      <div class="flex justify-between items-center py-1 border-b border-outline-variant/40">
                        <span class="font-body text-xs text-on-surface-variant">Est. Processing:</span>
                        <span id="station-sla-days" class="font-code text-xs font-bold text-primary">15–21 Days</span>
                      </div>
                      <div class="flex justify-between items-center py-1 border-b border-outline-variant/40">
                        <span class="font-body text-xs text-on-surface-variant">Statutory Fee:</span>
                        <span id="station-fee-amount" class="font-code text-xs font-bold text-primary">₹18,500.00</span>
                      </div>
                      <div class="flex justify-between items-center py-1">
                        <span class="font-body text-xs text-on-surface-variant">Prior Dependency:</span>
                        <span class="font-headline text-xs font-semibold text-emerald-700 flex items-center gap-1">
                          <span class="material-symbols-outlined text-[14px]">verified</span> Stop 02 Cleared
                        </span>
                      </div>
                    </div>
                    
                    <div class="space-y-2 pt-1">
                      <button onclick="window.app.inspectFullDossier()" class="w-full bg-primary hover:bg-primary-container text-on-primary font-headline text-xs font-semibold py-2.5 px-3 rounded-none flex items-center justify-center gap-1.5 transition-colors">
                        <span>Inspect Full Step Dossier</span>
                        <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                      </button>
                      <div class="text-center font-headline text-[10px] text-secondary">
                        Last updated Oct 2024 via MCGM Municipal Gateway
                      </div>
                    </div>
                  </div>
                </div>
              </article>

              <!-- PARALLEL INTERCHANGE CARDS (BRANCH 3A & 3B) -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- STOP 3A: FSSAI -->
                <article class="bg-surface-container-lowest p-4 rounded-none shadow-sm border-l-4 border-amber-400 border border-outline-variant cursor-pointer hover:bg-surface-container-low transition-colors" id="stop-03a" onclick="window.app.selectStation('mum-bakery-3a')">
                  <div class="flex items-center justify-between pb-1 mb-1">
                    <div class="flex items-center gap-1.5">
                      <span class="bg-secondary text-on-secondary font-code text-[11px] px-1.5 py-0.5">STOP 03A</span>
                      <span class="font-headline text-[10px] text-amber-800 bg-amber-50 px-2 py-0.5 font-semibold uppercase">Concurrent Track</span>
                    </div>
                    <span class="font-headline text-xs text-secondary font-medium">FSSAI MAHARASHTRA</span>
                  </div>
                  <h3 class="font-headline text-sm font-semibold text-primary mb-1">FSSAI State Food Business License</h3>
                  <p class="font-body text-xs text-on-surface-variant mb-2 leading-relaxed">
                    Mandatory Food Safety and Standards Authority of India (FSSAI) state operating license for commercial baking and food handling. Concurrent filing alongside MFB Fire audit.
                  </p>
                  <div class="flex items-center justify-between font-headline text-xs pt-2 border-t border-surface-container text-secondary">
                    <span>Fee: <strong class="text-primary font-code">₹7,500.00</strong></span>
                    <span>Window: <strong class="text-primary font-code">10–14 Days</strong></span>
                    <span class="text-primary font-semibold hover:underline">View Dossier</span>
                  </div>
                </article>

                <!-- STOP 3B: MPCB -->
                <article class="bg-surface-container-lowest p-4 rounded-none shadow-sm border-l-4 border-amber-400 border border-outline-variant cursor-pointer hover:bg-surface-container-low transition-colors" id="stop-03b" onclick="window.app.selectStation('mum-bakery-3b')">
                  <div class="flex items-center justify-between pb-1 mb-1">
                    <div class="flex items-center gap-1.5">
                      <span class="bg-secondary text-on-secondary font-code text-[11px] px-1.5 py-0.5">STOP 03B</span>
                      <span class="font-headline text-[10px] text-amber-800 bg-amber-50 px-2 py-0.5 font-semibold uppercase">Concurrent Track</span>
                    </div>
                    <span class="font-headline text-xs text-secondary font-medium">MPCB REGIONAL</span>
                  </div>
                  <h3 class="font-headline text-sm font-semibold text-primary mb-1">MPCB Pollution Consent (Green/Orange)</h3>
                  <p class="font-body text-xs text-on-surface-variant mb-2 leading-relaxed">
                    Maharashtra Pollution Control Board Consent to Establish and Operate. Effluent treatment discharge standards and grease interceptor approval for bakery washing sinks.
                  </p>
                  <div class="flex items-center justify-between font-headline text-xs pt-2 border-t border-surface-container text-secondary">
                    <span>Fee: <strong class="text-primary font-code">₹6,200.00</strong></span>
                    <span>Window: <strong class="text-primary font-code">7–12 Days</strong></span>
                    <span class="text-primary font-semibold hover:underline">View Dossier</span>
                  </div>
                </article>
              </div>

              <!-- UPCOMING DOWNSTREAM MILESTONES (STOPS 4, 5, 6) -->
              <div class="bg-surface-container-lowest p-4 rounded-none shadow-sm border border-outline-variant">
                <div class="font-headline text-xs font-bold uppercase text-primary mb-3 tracking-wide">
                  Downstream Stations (Locked Until Fire &amp; State Compliance Clearance)
                </div>
                <div class="divide-y divide-surface-container">
                  <!-- Stop 04 -->
                  <div class="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer hover:bg-surface-container-low transition-colors px-2" onclick="window.app.selectStation('mum-bakery-4')">
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-full bg-surface-container text-on-surface flex items-center justify-center font-code text-xs font-bold shrink-0">
                        04
                      </div>
                      <div>
                        <div class="flex items-center gap-2">
                          <span class="font-headline text-sm font-semibold text-primary">Pre-Operational Health Inspection (MOH)</span>
                          <span class="bg-surface-container text-on-surface-variant font-headline text-[10px] px-1.5 py-0.5 rounded">BMC MOH Ward H/W</span>
                        </div>
                        <p class="font-body text-xs text-on-surface-variant mt-0.5">
                          Physical on-site health inspection of food storage temperatures, hand-washing basins, pestproofing, and municipal water testing under § 394 of Mumbai Municipal Corporation Act.
                        </p>
                      </div>
                    </div>
                    <div class="text-right shrink-0">
                      <div class="font-headline text-[10px] text-outline uppercase font-semibold">Prerequisites</div>
                      <div class="font-code text-xs text-secondary">Stops 03, 03A, 03B</div>
                    </div>
                  </div>

                  <!-- Stop 05 -->
                  <div class="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer hover:bg-surface-container-low transition-colors px-2" onclick="window.app.selectStation('mum-bakery-5')">
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-full bg-surface-container text-on-surface flex items-center justify-center font-code text-xs font-bold shrink-0">
                        05
                      </div>
                      <div>
                        <div class="flex items-center gap-2">
                          <span class="font-headline text-sm font-semibold text-primary">Eating House License &amp; Signboard Permission</span>
                          <span class="bg-surface-container text-on-surface-variant font-headline text-[10px] px-1.5 py-0.5 rounded">MCGM / Mumbai Police</span>
                        </div>
                        <p class="font-body text-xs text-on-surface-variant mt-0.5">
                          Pedestrian clear-path verification and Mumbai Police Licensing Branch NOC for commercial premises and Marathi Devanagari signboard compliance.
                        </p>
                      </div>
                    </div>
                    <div class="text-right shrink-0">
                      <div class="font-headline text-[10px] text-outline uppercase font-semibold">Prerequisites</div>
                      <div class="font-code text-xs text-secondary">Stop 02, Stop 04</div>
                    </div>
                  </div>

                  <!-- Stop 06 -->
                  <div class="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer hover:bg-surface-container-low transition-colors px-2" onclick="window.app.selectStation('mum-bakery-6')">
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-full bg-primary text-on-primary flex items-center justify-center font-code text-xs font-bold shrink-0">
                        06
                      </div>
                      <div>
                        <div class="flex items-center gap-2">
                          <span class="font-headline text-sm font-bold text-primary">Final Municipal Trade Ledger Inscription &amp; Digital QR Seal</span>
                          <span class="bg-primary text-on-primary font-headline text-[10px] px-1.5 py-0.5 rounded uppercase">Terminus</span>
                        </div>
                        <p class="font-body text-xs text-on-surface-variant mt-0.5">
                          Unified municipal permit issuance granting full commercial operational standing and retail food service authorization with encrypted digital QR seal.
                        </p>
                      </div>
                    </div>
                    <div class="text-right shrink-0">
                      <div class="font-headline text-[10px] text-outline uppercase font-semibold">Statutory Standing</div>
                      <div class="font-code text-xs text-primary font-bold">Final Registry</div>
                    </div>
                  </div>
                </div>
              </div>

            </div>

          </div>

          <!-- Right 3 Columns: Side Utility & Immediate Action Fast Rail (Stitch Screen 2 Localized) -->
          <aside class="lg:col-span-3 flex flex-col space-y-4">
            
            <!-- Next Blocker Alert Card -->
            <div class="bg-surface-container-lowest p-4 rounded-none shadow-sm border-t-4 border-error border border-outline-variant">
              <div class="flex items-center gap-1.5 text-error mb-2">
                <span class="material-symbols-outlined text-[18px]">notification_important</span>
                <span class="font-headline text-xs font-bold uppercase tracking-wider">Next Blocker to Clear</span>
              </div>
              <div class="font-headline text-sm font-semibold text-primary mb-1">
                MFB Ward Inspection &amp; Duct Clearance Objection
              </div>
              <p class="font-body text-xs text-on-surface-variant mb-2 leading-relaxed">
                Plan examiner and MFB sub-officer issued compliance objection regarding duct termination clearance during preliminary site visit.
              </p>
              <div class="bg-error-container p-2 rounded-none text-on-error-container font-code text-[11px] mb-3 border border-red-200">
                Objection Notice: Sec 3(1) of Maharashtra Fire Act 2006 - Minimum 1.5m clearance between commercial exhaust termination and adjacent residential balcony.
              </div>
              <button onclick="alert('Submission portal opened for Chief Fire Officer (CFO) revised kitchen duct drawings.')" class="w-full bg-surface-container hover:bg-surface-container-high text-primary font-headline text-xs py-2 px-3 rounded-none flex items-center justify-center gap-1.5 transition-colors font-semibold border border-outline-variant">
                <span class="material-symbols-outlined text-[16px]">assignment_late</span>
                <span>Submit Revised Duct Layout to CFO</span>
              </button>
            </div>

            <!-- Physical Counter Desk & Working Hours -->
            <div class="bg-surface-container-lowest p-4 rounded-none shadow-sm border border-outline-variant">
              <div class="flex items-center gap-1.5 text-primary mb-2">
                <span class="material-symbols-outlined text-[18px]">business</span>
                <span class="font-headline text-xs font-bold uppercase tracking-wider">Agency Counter &amp; Desk</span>
              </div>
              <div class="font-headline text-sm font-semibold text-primary mb-1">
                MCGM Ward H/West Municipal Office
              </div>
              <div class="font-body text-xs text-on-surface-variant space-y-1">
                <p>Saint Martin Road, Behind Bandra Police Station, Bandra West, Mumbai 400050<br/>Counter Window 4 (Health &amp; Fire NOC Facilitation Wing)</p>
                <p class="font-semibold text-primary pt-1">Public Counter Hours:</p>
                <p class="font-code text-xs text-secondary">Monday – Friday<br/>10:00 AM – 2:30 PM IST</p>
                <p class="text-error font-medium text-[11px]">Strict Notice: No token issuance after 1:30 PM.</p>
              </div>
            </div>

            <!-- Pre-requisite Stations Quick List Rail -->
            <div class="bg-surface-container-lowest p-4 rounded-none shadow-sm border border-outline-variant space-y-2">
              <div class="flex items-center justify-between pb-1 border-b border-outline-variant">
                <div class="font-headline text-xs font-bold uppercase tracking-wider text-secondary">
                  Route Milestones
                </div>
                <span class="font-code text-[11px] text-primary font-bold" id="rail-milestones-count">8 Stops</span>
              </div>
              <div class="space-y-1 pt-1" id="rail-stations-list">
                <!-- Rendered dynamically by app.js -->
              </div>
            </div>

          </aside>
        </div>

      </section>

      <!-- ==================================================================
           VIEW 3: STEP DOSSIER (Stitch Screen 3 Localized Precision)
           ================================================================== -->
      <section id="view-step-dossier" class="tab-pane flex flex-col w-full" style="display:none;">
        
        <!-- Navigational Docket Header & Path Sequence -->
        <div class="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-2 pb-2 border-b border-outline-variant">
          <nav aria-label="Jurisdictional Path" class="flex items-center gap-1.5 font-headline text-xs text-secondary">
            <a class="hover:text-primary transition-colors cursor-pointer" onclick="window.app.switchNavTab('task-lookup')">Docket Route</a>
            <span class="text-outline-variant">/</span>
            <a class="hover:text-primary transition-colors cursor-pointer" id="dossier-route-crumb" onclick="window.app.switchNavTab('roadmap-and-route')">Commercial Bakery &amp; Cafe Bandra</a>
            <span class="text-outline-variant">/</span>
            <span class="font-semibold text-primary" id="dossier-step-crumb">Stop 03 (BMC Health Trade License under Section 394 MMC Act)</span>
          </nav>
          <div class="flex items-center gap-2">
            <span class="font-code text-xs text-secondary" id="dossier-ref-code">REF: MCGM-HTL-2024-W-HW-90412</span>
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-outline-variant"></span>
            <span class="font-headline text-[11px] text-outline uppercase tracking-wider font-semibold">Priority Statutory Ledger</span>
          </div>
        </div>

        <!-- Primary Administrative Dossier Title Header (Stitch Screen 3) -->
        <div class="bg-surface-container-lowest border border-outline-variant p-6 mb-6 relative overflow-hidden shadow-sm">
          <div class="absolute top-0 left-0 right-0 h-1 bg-primary"></div>
          <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
            <div class="space-y-1.5 max-w-3xl">
              <div class="flex flex-wrap items-center gap-2">
                <span class="font-code text-xs bg-primary text-on-primary px-2 py-0.5 font-medium rounded-none" id="dossier-stage-idx">STAGE 03 / 08</span>
                <span class="font-headline text-xs uppercase tracking-wider text-secondary font-semibold" id="dossier-agency-name">MCGM PUBLIC HEALTH DEPARTMENT — WARD H/WEST</span>
              </div>
              <h1 class="font-headline text-2xl md:text-3xl text-primary tracking-tight font-semibold" id="dossier-main-title">
                Step 03: Apply for BMC Health Trade License (Section 394)
              </h1>
              <p class="font-body text-base text-on-surface-variant leading-relaxed" id="dossier-main-desc">
                Mandatory statutory trade authorization for operating a commercial bakery and food preparation establishment pursuant to Section 394 of the Mumbai Municipal Corporation Act (MMC Act, 1888).
              </p>
            </div>
            <!-- Active Docket Status Badge -->
            <div class="flex flex-col items-start lg:items-end gap-1 bg-surface-container-low p-4 border border-outline-variant min-w-[280px]">
              <div class="flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse" id="dossier-status-dot"></span>
                <span class="font-headline text-xs uppercase text-secondary font-semibold">Current Audit Status</span>
              </div>
              <div class="font-headline text-sm text-primary font-semibold" id="dossier-status-text">
                In Progress: Awaiting CFO Fire Safety NOC &amp; Site Inspection
              </div>
              <span class="font-code text-xs text-outline" id="dossier-status-sla">Target Filing Window: 14 Working Days</span>
            </div>
          </div>
          <!-- Official Provenance Authority Banner -->
          <div class="mt-6 pt-3 border-t border-outline-variant bg-surface-container-low -mx-6 -mb-6 px-6 py-2.5 flex flex-col md:flex-row items-start md:items-center justify-between gap-2">
            <div class="flex items-center gap-2 text-secondary font-body text-xs" id="dossier-provenance-text">
              <span class="material-symbols-outlined text-[18px] text-primary" style="font-variation-settings: 'FILL' 1;">gavel</span>
              <span>Verified against Municipal Corporation of Greater Mumbai Public Health Regulations as of <strong>October 2024</strong>.</span>
            </div>
            <a class="font-code text-xs text-primary underline hover:text-secondary inline-flex items-center gap-1 font-medium" href="https://portal.mcgm.gov.in/eodb-trade-license" id="dossier-provenance-link" rel="noopener noreferrer" target="_blank">
              <span id="dossier-provenance-link-text">portal.mcgm.gov.in/eodb-trade-license</span>
              <span class="material-symbols-outlined text-[13px]">open_in_new</span>
            </a>
          </div>
        </div>

        <!-- Prerequisite Chain Clearance Bar -->
        <div class="bg-surface-container-low border border-outline-variant p-4 mb-6">
          <div class="flex items-center justify-between flex-wrap gap-2 mb-2">
            <div class="flex items-center gap-1.5 font-headline text-xs text-primary font-semibold uppercase tracking-wider">
              <span class="material-symbols-outlined text-[16px] text-emerald-700">link</span>
              <span>Prerequisite Dependency Ledger</span>
            </div>
            <span class="font-code text-xs text-secondary" id="dossier-prereq-chain-status">CHAIN STATUS: 2/2 SATISFIED</span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1" id="dossier-prereqs-grid">
            <div class="bg-surface-container-lowest p-3 border border-outline-variant flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <span class="w-5 h-5 rounded-full bg-emerald-800 text-on-primary flex items-center justify-center font-code text-[11px] font-bold">✓</span>
                <div>
                  <div class="font-headline text-xs text-primary font-semibold">Stop 01: MCA Incorporation &amp; GSTIN Registration</div>
                  <div class="font-code text-[11px] text-secondary">CIN: U15100MH2024PTC392810 • Verified RoC Mumbai</div>
                </div>
              </div>
              <span class="font-headline text-[10px] bg-emerald-100 text-emerald-900 border border-emerald-300 px-2 py-0.5 font-semibold">Cleared</span>
            </div>
            <div class="bg-surface-container-lowest p-3 border border-outline-variant flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <span class="w-5 h-5 rounded-full bg-emerald-800 text-on-primary flex items-center justify-center font-code text-[11px] font-bold">✓</span>
                <div>
                  <div class="font-headline text-xs text-primary font-semibold">Stop 02: Maharashtra Shops &amp; Establishments Gumasta</div>
                  <div class="font-code text-[11px] text-secondary">Registration #MH-MUM-HW-2024-44109 • Verified Aaple Sarkar</div>
                </div>
              </div>
              <span class="font-headline text-[10px] bg-emerald-100 text-emerald-900 border border-emerald-300 px-2 py-0.5 font-semibold">Cleared</span>
            </div>
          </div>
        </div>

        <!-- Primary 12-Column Split: 8 Col Evidence & Specifications / 4 Col Action & Municipal Counter -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          <!-- LEFT 8 COLUMNS: Statutory Mandates, Forms, Evidence Checklists & Fees -->
          <div class="lg:col-span-8 space-y-6">
            
            <!-- Section 1: Required Statutory Forms -->
            <section class="bg-surface-container-lowest border border-outline-variant shadow-sm">
              <div class="bg-surface-container-low px-4 py-2.5 border-b border-outline-variant flex items-center justify-between">
                <div class="flex items-center gap-1.5 font-headline text-xs text-primary font-semibold uppercase tracking-wider">
                  <span class="material-symbols-outlined text-[18px]">description</span>
                  <span>1. Mandatory Statutory Forms</span>
                </div>
                <span class="font-headline text-xs text-secondary" id="dossier-forms-count">3 Prescribed Instruments</span>
              </div>
              <div class="p-4 divide-y divide-outline-variant" id="dossier-forms-container">
                <!-- Item 1.1: FORM HTL-1 -->
                <div class="py-3 first:pt-0 last:pb-0 flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div class="space-y-1 max-w-xl">
                    <div class="flex items-center gap-2">
                      <span class="font-code text-xs font-semibold bg-surface-container px-2 py-0.5 border border-outline-variant text-primary">FORM HTL-1</span>
                      <h3 class="font-headline text-sm font-semibold text-primary">Application for Health Trade License under Section 394 (MMC Act 1888)</h3>
                    </div>
                    <p class="font-body text-xs text-on-surface-variant leading-relaxed">Prescribed composite application covering trade premises, water connection assessment, trade refuse charges, and power load (HP) sanction.</p>
                    <div class="font-code text-[11px] text-secondary">MMC Act 1888 • Required Original Signatures &amp; Ward H/West Attestation</div>
                  </div>
                  <a class="inline-flex items-center justify-center gap-1.5 bg-surface-container-lowest text-primary border border-outline hover:bg-surface-container-low px-4 py-2 font-headline text-xs font-semibold transition-colors shrink-0" href="https://portal.mcgm.gov.in" target="_blank">
                    <span class="material-symbols-outlined text-[16px]">download</span>
                    <span>Official PDF (740 KB)</span>
                  </a>
                </div>
                <!-- Item 1.2: FORM FSSAI-B -->
                <div class="py-3 last:pb-0 flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div class="space-y-1 max-w-xl">
                    <div class="flex items-center gap-2">
                      <span class="font-code text-xs font-semibold bg-surface-container px-2 py-0.5 border border-outline-variant text-primary">FORM FSSAI-B</span>
                      <h3 class="font-headline text-sm font-semibold text-primary">Schedule 2 Form B Application for FSSAI State License</h3>
                    </div>
                    <p class="font-body text-xs text-on-surface-variant leading-relaxed">Food safety compliance instrument specifying food categories, installed capacity (MT/day), clean water source test report, and food handler medical fitness.</p>
                    <div class="font-code text-[11px] text-secondary">Food Safety and Standards Authority of India (Maharashtra State Jurisdiction)</div>
                  </div>
                  <a class="inline-flex items-center justify-center gap-1.5 bg-surface-container-lowest text-primary border border-outline hover:bg-surface-container-low px-4 py-2 font-headline text-xs font-semibold transition-colors shrink-0" href="https://foscos.fssai.gov.in" target="_blank">
                    <span class="material-symbols-outlined text-[16px]">download</span>
                    <span>Official PDF (510 KB)</span>
                  </a>
                </div>
                <!-- Item 1.3: ANNEXURE C -->
                <div class="py-3 last:pb-0 flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div class="space-y-1 max-w-xl">
                    <div class="flex items-center gap-2">
                      <span class="font-code text-xs font-semibold bg-surface-container px-2 py-0.5 border border-outline-variant text-primary">ANNEXURE C</span>
                      <h3 class="font-headline text-sm font-semibold text-primary">Mumbai Fire Brigade (MFB) Fire Safety &amp; Kitchen Ventilation Declaration</h3>
                    </div>
                    <p class="font-body text-xs text-on-surface-variant leading-relaxed">Architectural layout showing grease filters, chimney height (3m above roof parapet), LPG manifold manifold clearance, and Class-K wet chemical fire system.</p>
                    <div class="font-code text-[11px] text-secondary">Must Comply with Maharashtra Fire Prevention and Life Safety Measures Act</div>
                  </div>
                  <a class="inline-flex items-center justify-center gap-1.5 bg-surface-container-lowest text-primary border border-outline hover:bg-surface-container-low px-4 py-2 font-headline text-xs font-semibold transition-colors shrink-0" href="https://portal.mcgm.gov.in/eodb-fire-noc" target="_blank">
                    <span class="material-symbols-outlined text-[16px]">download</span>
                    <span>Official PDF (480 KB)</span>
                  </a>
                </div>
              </div>
            </section>

            <!-- Section 2: Mandatory Documentation & Evidence Ledger -->
            <section class="bg-surface-container-lowest border border-outline-variant shadow-sm">
              <div class="bg-surface-container-low px-4 py-2.5 border-b border-outline-variant flex items-center justify-between">
                <div class="flex items-center gap-1.5 font-headline text-xs text-primary font-semibold uppercase tracking-wider">
                  <span class="material-symbols-outlined text-[18px]">inventory_2</span>
                  <span>2. Mandatory Evidence &amp; Sealed Filings</span>
                </div>
                <span class="font-headline text-xs text-secondary" id="dossier-evidence-count">3 Evidence Criteria</span>
              </div>
              <div class="p-4 space-y-4" id="dossier-evidence-container">
                <!-- Evidence 1 -->
                <div class="p-3 bg-surface-container-lowest border border-outline-variant flex flex-col md:flex-row items-start justify-between gap-3">
                  <div class="space-y-1 max-w-xl">
                    <div class="flex items-center gap-2">
                      <span class="material-symbols-outlined text-amber-700 text-[18px]">pending</span>
                      <span class="font-headline text-sm font-semibold text-primary">Sealed Architectural Layout &amp; MEP Drawing</span>
                    </div>
                    <p class="font-body text-xs text-on-surface-variant leading-relaxed">Prepared and stamped by a licensed architect / MCGM registered structural engineer. Showing customer seating, bakery oven zoning, refuse disposal, and fire exit doors.</p>
                    <div class="font-code text-[11px] text-outline">CRITERIA: Title block must reference CTS Number, Bandra West Ward H/West</div>
                  </div>
                  <div class="shrink-0 flex flex-col items-start md:items-end gap-1">
                    <span class="font-headline text-[10px] bg-amber-50 text-amber-900 border border-amber-300 px-2 py-0.5 font-semibold">Action Required</span>
                    <button class="font-headline text-xs text-primary underline hover:text-secondary font-medium mt-1" onclick="alert('Upload Portal: Please select signed architectural CAD or PDF plan set (<25MB).')">Upload Encrypted CAD/PDF</button>
                  </div>
                </div>
                <!-- Evidence 2 -->
                <div class="p-3 bg-surface-container-lowest border border-outline-variant flex flex-col md:flex-row items-start justify-between gap-3">
                  <div class="space-y-1 max-w-xl">
                    <div class="flex items-center gap-2">
                      <span class="material-symbols-outlined text-emerald-800 text-[18px]">check_circle</span>
                      <span class="font-headline text-sm font-semibold text-primary">MPCB Consent to Establish (Green/Orange Category)</span>
                    </div>
                    <p class="font-body text-xs text-on-surface-variant leading-relaxed">Pollution board authorization for commercial bakery baking equipment, effluent treatment for kitchen sink wash, and noise attenuation.</p>
                    <div class="font-code text-[11px] text-emerald-800 font-medium">MPCB ID: #MPCB-CONSENT-MUM-2024-9182 • Logged &amp; Cryptographically Tied</div>
                  </div>
                  <div class="shrink-0 flex flex-col items-start md:items-end gap-1">
                    <span class="font-headline text-[10px] bg-emerald-100 text-emerald-900 border border-emerald-300 px-2 py-0.5 font-semibold">Verified on File</span>
                    <span class="font-code text-[10px] text-secondary">Verified Oct 14, 2024</span>
                  </div>
                </div>
                <!-- Evidence 3 -->
                <div class="p-3 bg-surface-container-lowest border border-outline-variant flex flex-col md:flex-row items-start justify-between gap-3">
                  <div class="space-y-1 max-w-xl">
                    <div class="flex items-center gap-2">
                      <span class="material-symbols-outlined text-emerald-800 text-[18px]">check_circle</span>
                      <span class="font-headline text-sm font-semibold text-primary">Pest Control Contract &amp; Water Potability Certificate</span>
                    </div>
                    <p class="font-body text-xs text-on-surface-variant leading-relaxed">Certified contract with government-approved pest control operator and BMC bacteriological water test report from Municipal Laboratory, Dadar.</p>
                    <div class="font-code text-[11px] text-secondary">Statutory Compliance: MMC Act § 394 &amp; BMC Health By-Laws</div>
                  </div>
                  <div class="shrink-0 flex flex-col items-start md:items-end gap-1">
                    <span class="font-headline text-[10px] bg-emerald-100 text-emerald-900 border border-emerald-300 px-2 py-0.5 font-semibold">Notice Drafted</span>
                    <span class="font-code text-[10px] text-secondary">Certificate Ready</span>
                  </div>
                </div>
              </div>
            </section>

            <!-- Section 3: Statutory Municipal Fee Breakdown Ledger (Stitch Screen 3) -->
            <section class="bg-surface-container-lowest border border-outline-variant shadow-sm">
              <div class="bg-surface-container-low px-4 py-2.5 border-b border-outline-variant flex items-center justify-between">
                <div class="flex items-center gap-1.5 font-headline text-xs text-primary font-semibold uppercase tracking-wider">
                  <span class="material-symbols-outlined text-[18px]">receipt_long</span>
                  <span>3. Statutory Municipal Fee Breakdown</span>
                </div>
                <span class="font-code text-xs text-secondary">MMC ACT &amp; MFB SCHEDULE</span>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                  <thead>
                    <tr class="bg-surface-container-low font-headline text-[11px] text-primary uppercase border-b border-outline-variant">
                      <th class="py-2 px-4">Administrative Line Item</th>
                      <th class="py-2 px-4">Statutory Basis</th>
                      <th class="py-2 px-4 text-right">Calculation Factor</th>
                      <th class="py-2 px-4 text-right">Amount (INR ₹)</th>
                    </tr>
                  </thead>
                  <tbody class="font-body text-xs divide-y divide-outline-variant" id="dossier-fee-table-body">
                    <tr class="hover:bg-surface-container-lowest">
                      <td class="py-2.5 px-4 font-semibold text-primary">Section 394 Trade License Fee (Bakery with Power)</td>
                      <td class="py-2.5 px-4 text-secondary">MMC Act § 394 Schedule M</td>
                      <td class="py-2.5 px-4 text-right font-code text-xs">Commercial Food Prep Base</td>
                      <td class="py-2.5 px-4 text-right font-code text-xs font-semibold text-primary">₹14,500.00</td>
                    </tr>
                    <tr class="hover:bg-surface-container-lowest">
                      <td class="py-2.5 px-4 font-semibold text-primary">Trade Refuse Charge (TRC) Annual Assessment</td>
                      <td class="py-2.5 px-4 text-secondary">MCGM Solid Waste Mgmt Rules 2016</td>
                      <td class="py-2.5 px-4 text-right font-code text-xs">Commercial Wet/Dry Waste Levy</td>
                      <td class="py-2.5 px-4 text-right font-code text-xs font-semibold text-primary">₹8,400.00</td>
                    </tr>
                    <tr class="hover:bg-surface-container-lowest">
                      <td class="py-2.5 px-4 font-semibold text-primary">Fire Safety Compliance &amp; Inspection Surcharge</td>
                      <td class="py-2.5 px-4 text-secondary">Maharashtra Fire Act § 13</td>
                      <td class="py-2.5 px-4 text-right font-code text-xs">MFB Kitchen Inspection Assessment</td>
                      <td class="py-2.5 px-4 text-right font-code text-xs font-semibold text-primary">₹6,200.00</td>
                    </tr>
                    <tr class="hover:bg-surface-container-lowest">
                      <td class="py-2.5 px-4 font-semibold text-primary">Factory / Power Machinery Inspection (5 HP Baking Deck)</td>
                      <td class="py-2.5 px-4 text-secondary">BMC Industrial Power Schedule</td>
                      <td class="py-2.5 px-4 text-right font-code text-xs">5 HP Load Assessment</td>
                      <td class="py-2.5 px-4 text-right font-code text-xs font-semibold text-primary">₹3,800.00</td>
                    </tr>
                  </tbody>
                  <tfoot>
                    <tr class="bg-surface-container-low font-headline text-xs border-t-2 border-primary">
                      <td class="py-2.5 px-4 font-bold text-primary text-right uppercase tracking-wider" colspan="3">
                        Total Municipal Fee Payable to BMC Collector:
                      </td>
                      <td class="py-2.5 px-4 text-right font-code text-base font-bold text-primary" id="dossier-fee-total">
                        ₹32,900.00
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
              <div class="p-3 bg-surface-container text-secondary font-headline text-[11px] border-t border-outline-variant flex items-center justify-between">
                <span>Acceptable Tender: MCGM Citizen Portal Online Payment, NetBanking (SBI/HDFC), or Treasury Challan at Ward H/West Citizen Facilitation Centre (CFC).</span>
                <span class="font-code font-bold">NO CASH OVER ₹10,000</span>
              </div>
            </section>

            <!-- Section 4: Statutory Legal Notes and Standard Operating Guidelines -->
            <section class="border border-outline-variant bg-surface-container-lowest p-4 space-y-1 shadow-sm">
              <h4 class="font-headline text-xs uppercase font-semibold tracking-wider text-secondary">Statutory Operating Directive: Mechanical Kitchen Exhaust &amp; Fire Norms</h4>
              <p class="font-body text-xs text-on-surface-variant leading-relaxed" id="dossier-guidelines-text">
                Pursuant to Section 394 of the Mumbai Municipal Corporation Act and Mumbai Fire Brigade directives, commercial bakery installations utilizing ovens or frying assemblies emitting grease or heat must maintain a dedicated stainless steel hood ducted directly to 3 meters above the building parapet. Clearances from adjoining tenements and residential window openings must conform to MCGM Health By-laws. Failure to provide endorsed MEP drawings and MFB CFO clearance will cause immediate rejection of the health trade docket.
              </p>
            </section>

          </div>

          <!-- RIGHT 4 COLUMNS: Action Execution Box, Physical Counter Wayfinding, Ombudsman (Stitch Screen 3) -->
          <div class="lg:col-span-4 space-y-6">
            
            <!-- Action Center Dossier Box (High Priority Action Card) -->
            <div class="bg-surface-container-lowest border-2 border-primary shadow-[4px_4px_0px_0px_rgba(21,34,56,0.15)] p-4">
              <div class="flex items-center justify-between pb-2 border-b border-outline-variant mb-4">
                <span class="font-headline text-xs font-bold uppercase tracking-wider text-primary">Docket Action Portal</span>
                <span class="w-2 h-2 bg-emerald-600 rounded-full"></span>
              </div>
              <div class="space-y-4">
                <div>
                  <label class="block font-headline text-xs text-primary font-semibold mb-1" for="mcgm-app-num">
                    MCGM Citizen File / Application Number
                  </label>
                  <div class="relative">
                    <input class="w-full bg-surface-container-lowest border border-outline px-3 py-2 font-code text-xs text-primary focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent rounded-none" id="mcgm-app-num" maxlength="10" placeholder="e.g. 7204918204" type="text"/>
                    <button class="absolute right-2 top-2 text-outline hover:text-primary" title="Search MCGM Citizen Portal Database">
                      <span class="material-symbols-outlined text-[18px]">search</span>
                    </button>
                  </div>
                  <p class="font-body text-xs text-secondary mt-1 italic">Enter the 10-digit MCGM citizen portal application number from your preliminary filing acknowledgement.</p>
                </div>
                <div class="pt-1 space-y-2">
                  <button class="w-full bg-primary text-on-primary hover:bg-primary-container px-4 py-3 font-headline text-xs font-semibold tracking-wide border border-primary transition-colors flex items-center justify-center gap-2" id="btn-advance-route" onclick="window.app.advanceStepAction()">
                    <span class="material-symbols-outlined text-[18px]">verified</span>
                    <span id="btn-advance-label">Mark Step Complete &amp; Advance</span>
                  </button>
                  <button class="w-full bg-surface-container-lowest text-primary hover:bg-surface-container-low px-4 py-2 font-headline text-xs font-semibold border border-outline transition-colors flex items-center justify-center gap-1.5" onclick="alert('Upload Portal: Please select your official Treasury Challan bank receipt stamp.')">
                    <span class="material-symbols-outlined text-[16px]">upload_file</span>
                    <span>Upload Municipal CFC Challan Receipt</span>
                  </button>
                </div>
                <div class="pt-2 border-t border-outline-variant">
                  <div class="flex items-start gap-1.5 text-secondary font-headline text-[11px]">
                    <span class="material-symbols-outlined text-[16px] text-amber-700 shrink-0 mt-0.5">info</span>
                    <span>Making a false declaration or operating without a valid Section 394 license attracts prosecution under Section 471 of MMC Act 1888.</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Physical Municipal Counter & Agency Wayfinding (Stitch Screen 3) -->
            <div class="bg-surface-container-lowest border border-outline-variant shadow-sm">
              <div class="bg-surface-container-low px-4 py-2.5 border-b border-outline-variant flex items-center justify-between">
                <div class="flex items-center gap-1.5 font-headline text-xs text-primary font-semibold uppercase tracking-wider">
                  <span class="material-symbols-outlined text-[18px]">domain</span>
                  <span>Public Window &amp; Ward Office</span>
                </div>
                <span class="font-code text-xs text-secondary" id="dossier-office-borough">WARD H/WEST</span>
              </div>
              <div class="p-4 space-y-4">
                <div class="space-y-1">
                  <div class="font-headline text-[11px] text-outline uppercase font-semibold">Physical Filing Address</div>
                  <div class="font-headline text-sm font-semibold text-primary" id="dossier-office-address">MCGM Ward H/West Office (Bandra West)</div>
                  <div class="font-body text-xs text-on-surface-variant" id="dossier-office-window">CFC Window 4 (Health Trade &amp; License Wing)</div>
                  <div class="font-code text-xs text-secondary" id="dossier-office-city">Saint Martin Road, Behind Bandra Police Station, Bandra West, Mumbai, Maharashtra 400050</div>
                </div>
                <div class="border-t border-outline-variant pt-2 space-y-1">
                  <div class="font-headline text-[11px] text-outline uppercase font-semibold">Public Counter Hours</div>
                  <div class="font-headline text-xs text-primary font-semibold" id="dossier-office-hours">Monday – Friday: 10:00 AM – 2:30 PM IST</div>
                  <div class="font-body text-xs text-error font-medium">Strict Notice: No token issuance after 1:30 PM.</div>
                </div>
                <div class="border-t border-outline-variant pt-2 space-y-1">
                  <div class="font-headline text-[11px] text-outline uppercase font-semibold">Mandatory In-Person Intake Protocol</div>
                  <ul class="font-body text-xs text-on-surface-variant space-y-1">
                    <li class="flex items-start gap-1.5">
                      <span class="text-primary font-bold">•</span>
                      <span>Bring <strong>2 hard copies of verified plan sets</strong> signed by MCGM Registered Architect.</span>
                    </li>
                    <li class="flex items-start gap-1.5">
                      <span class="text-primary font-bold">•</span>
                      <span>1 Pen Drive with digital <strong>PDF files</strong> (&lt;25MB each).</span>
                    </li>
                    <li class="flex items-start gap-1.5">
                      <span class="text-primary font-bold">•</span>
                      <span>Director KYC/Aadhaar cards and entity commercial lease agreement.</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Direct Assistance & Agency Ombudsman (Stitch Screen 3) -->
            <div class="bg-surface-container-low border border-outline-variant p-4 space-y-2 shadow-sm">
              <div class="flex items-center gap-1.5 font-headline text-xs text-primary font-semibold uppercase tracking-wider">
                <span class="material-symbols-outlined text-[18px]">support_agent</span>
                <span>MCGM Industry &amp; Trade Facilitation Cell</span>
              </div>
              <p class="font-body text-xs text-on-surface-variant leading-relaxed">
                Dedicated MCGM ease of doing business officers assist food operators with health inspection protocols and online application scrutinies.
              </p>
              <div class="bg-surface-container-lowest p-2.5 border border-outline-variant space-y-1">
                <div class="flex items-center justify-between font-headline text-xs">
                  <span class="text-secondary">Direct Telephone:</span>
                  <span class="font-code font-semibold text-primary" id="dossier-ombuds-phone">(022) 2642-2311</span>
                </div>
                <div class="flex items-center justify-between font-headline text-xs">
                  <span class="text-secondary">Expedited Email:</span>
                  <span class="font-code text-primary underline truncate ml-2" id="dossier-ombuds-email">eodb.support@mcgm.gov.in</span>
                </div>
              </div>
              <div class="font-code text-outline text-[11px] pt-1">
                AVERAGE INQUIRY RESOLUTION: 48 WORKING HOURS
              </div>
            </div>

          </div>

        </div>

      </section>

      <!-- ==================================================================
           VIEW 4: CITIZEN LEDGER & AUDIT TRAIL (Localizing for Indian Receipts)
           ================================================================== -->
      <section id="view-citizen-ledger" class="tab-pane flex flex-col w-full" style="display:none;">
        
        <div class="bg-surface-container-lowest p-6 border border-outline-variant shadow-sm mb-6">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-outline-variant">
            <div>
              <div class="font-headline text-[11px] font-semibold text-secondary uppercase tracking-widest mb-1">
                Public Statutory Registry &amp; Citizen Ledger
              </div>
              <h1 class="font-headline text-2xl md:text-3xl text-primary font-semibold tracking-tight">
                Municipal Compliance Ledger &amp; Receipts
              </h1>
              <p class="font-body text-xs text-on-surface-variant mt-1">
                Cryptographically audited municipal filing log conforming to Maharashtra Right to Public Services Act 2015. Certified receipts carry SHA-256 verification hashes.
              </p>
            </div>
            <div class="flex items-center gap-2">
              <button class="bg-surface-container hover:bg-surface-container-high text-primary px-3 py-2 font-headline text-xs font-semibold border border-outline-variant flex items-center gap-1.5" onclick="alert('DigiLocker Integration: In a production environment, all verified certificates are synced directly with citizen DigiLocker account (Government of India).')">
                <span class="material-symbols-outlined text-[16px] text-blue-700">cloud_done</span>
                <span>DigiLocker Sync</span>
              </button>
              <button class="bg-primary text-on-primary px-4 py-2 font-headline text-xs font-semibold hover:bg-primary-container flex items-center gap-1.5" onclick="window.print()">
                <span class="material-symbols-outlined text-[16px]">receipt</span>
                <span>Export Tax Receipt</span>
              </button>
            </div>
          </div>

          <!-- Ledger Metrics Ribbon -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
            <div class="bg-surface-container-low p-3 border border-outline-variant">
              <div class="font-headline text-[11px] text-secondary uppercase font-semibold">Total Milestones</div>
              <div class="font-headline text-lg text-primary font-bold" id="ledger-total-milestones">8 Stations</div>
            </div>
            <div class="bg-surface-container-low p-3 border border-outline-variant">
              <div class="font-headline text-[11px] text-secondary uppercase font-semibold">Cleared Milestones</div>
              <div class="font-headline text-lg text-emerald-800 font-bold" id="ledger-cleared-milestones">2 Cleared (25%)</div>
            </div>
            <div class="bg-surface-container-low p-3 border border-outline-variant">
              <div class="font-headline text-[11px] text-secondary uppercase font-semibold">Total Statutory Fees</div>
              <div class="font-headline text-lg text-primary font-bold" id="ledger-total-fees">₹52,400.00 Base</div>
            </div>
          </div>
        </div>

        <!-- Ledger Entries Table -->
        <div class="bg-surface-container-lowest border border-outline-variant shadow-sm overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-surface-container-low font-headline text-[11px] text-primary uppercase border-b border-outline-variant">
                <th class="py-2.5 px-4">Stop</th>
                <th class="py-2.5 px-4">Statutory Procedure</th>
                <th class="py-2.5 px-4">Department</th>
                <th class="py-2.5 px-4">Docket Ref</th>
                <th class="py-2.5 px-4">Challan Fee (₹)</th>
                <th class="py-2.5 px-4">Status &amp; Verification</th>
                <th class="py-2.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-variant font-headline text-xs" id="citizen-ledger-table-body">
              <!-- Dynamically rendered by app.js -->
            </tbody>
          </table>
        </div>

      </section>

      <!-- ==================================================================
           VIEW 5: REGISTRY ADMIN & CRAWLER TERMINAL
           ================================================================== -->
      <section id="view-registry-admin" class="tab-pane flex flex-col w-full" style="display:none;">
        
        <div class="bg-surface-container-lowest p-6 border border-outline-variant shadow-sm mb-6">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-outline-variant">
            <div>
              <div class="font-headline text-[11px] font-semibold text-secondary uppercase tracking-widest mb-1">
                Registry Administration &amp; Portal Ingestion Gateway
              </div>
              <h1 class="font-headline text-2xl md:text-3xl text-primary font-semibold tracking-tight">
                Municipal Scraper &amp; Verification Console
              </h1>
              <p class="font-body text-xs text-on-surface-variant mt-1">
                Synchronizes and audits regulatory fee schedules, prescribed PDF instruments, and jurisdictional requirements directly from official Indian government portals.
              </p>
            </div>
            <div class="flex items-center gap-2">
              <span class="bg-surface-container px-2.5 py-1 text-xs font-code border border-outline-variant text-primary font-semibold">
                NODE: MUM-W-HW
              </span>
            </div>
          </div>

          <!-- Admin Sub-Navigation -->
          <div class="flex gap-2 pt-4 border-b border-outline-variant">
            <button class="admin-subtab px-4 py-2 font-headline text-xs font-semibold active border-b-2 border-primary text-primary bg-surface-container-low" data-subtab="scraper" onclick="window.adminManager.switchTab('scraper')">
              Portal Crawler Terminal
            </button>
            <button class="admin-subtab px-4 py-2 font-headline text-xs font-semibold border-b-2 border-transparent text-secondary hover:text-primary" data-subtab="moderation" onclick="window.adminManager.switchTab('moderation')">
              Step Verification &amp; Fee Queue
            </button>
            <button class="admin-subtab px-4 py-2 font-headline text-xs font-semibold border-b-2 border-transparent text-secondary hover:text-primary" data-subtab="audit" onclick="window.adminManager.switchTab('audit')">
              Statutory Audit Logs
            </button>
            <button class="admin-subtab px-4 py-2 font-headline text-xs font-semibold border-b-2 border-transparent text-secondary hover:text-primary" data-subtab="feedback" onclick="window.adminManager.switchTab('feedback')">
              Citizen Discrepancy Reports
            </button>
          </div>
        </div>

        <!-- Tab 5.1: Portal Scraper Console -->
        <div class="admin-tab-pane space-y-6" id="pane-scraper">
          <div class="bg-surface-container-lowest p-6 border border-outline-variant shadow-sm space-y-4">
            <div class="font-headline text-sm font-semibold text-primary uppercase tracking-wide">
              Official Indian Municipal Portal Ingestion &amp; Verification
            </div>
            <p class="font-body text-xs text-on-surface-variant">
              Enter any official municipal or state portal URL to execute an automated audit crawler that extracts statutory fees, application forms, physical window addresses, and prerequisite criteria.
            </p>

            <!-- Quick Presets -->
            <div class="flex flex-wrap gap-2 pt-1">
              <span class="font-headline text-xs text-secondary self-center mr-1">Quick Presets:</span>
              <button class="preset-btn bg-surface-container hover:bg-surface-container-high px-2.5 py-1 text-xs font-headline font-semibold text-primary border border-outline-variant" data-url="https://portal.mcgm.gov.in/eodb-trade-license" data-hint="Commercial Bakery Section 394 Health License">
                MCGM Health Trade (§ 394)
              </button>
              <button class="preset-btn bg-surface-container hover:bg-surface-container-high px-2.5 py-1 text-xs font-headline font-semibold text-primary border border-outline-variant" data-url="https://aaplesarkar.mahaonline.gov.in" data-hint="Maharashtra Shops Act Gumasta Registration">
                Aaple Sarkar (Gumasta)
              </button>
              <button class="preset-btn bg-surface-container hover:bg-surface-container-high px-2.5 py-1 text-xs font-headline font-semibold text-primary border border-outline-variant" data-url="https://foscos.fssai.gov.in" data-hint="FSSAI State Food License Schedule 2 Form B">
                FSSAI FoSCoS
              </button>
              <button class="preset-btn bg-surface-container hover:bg-surface-container-high px-2.5 py-1 text-xs font-headline font-semibold text-primary border border-outline-variant" data-url="https://mpcb.gov.in" data-hint="MPCB Pollution Consent to Establish CTE Green Category">
                MPCB Pollution
              </button>
              <button class="preset-btn bg-surface-container hover:bg-surface-container-high px-2.5 py-1 text-xs font-headline font-semibold text-primary border border-outline-variant" data-url="https://bbmp.karnataka.gov.in" data-hint="BBMP Trade License Bengaluru">
                BBMP Bengaluru
              </button>
              <button class="preset-btn bg-surface-container hover:bg-surface-container-high px-2.5 py-1 text-xs font-headline font-semibold text-primary border border-outline-variant" data-url="https://mcdonline.nic.in" data-hint="MCD Delhi Property Tax Mutation">
                MCD Delhi
              </button>
            </div>

            <!-- Ingestion Form -->
            <div class="grid grid-cols-1 md:grid-cols-12 gap-3 pt-2">
              <div class="md:col-span-8">
                <input class="w-full bg-surface-container-lowest border border-outline px-3 py-2 font-code text-xs text-primary focus:outline-none focus:ring-1 focus:ring-primary rounded-none" id="scraper-url-input" placeholder="https://portal.mcgm.gov.in/eodb-trade-license" type="url" value="https://portal.mcgm.gov.in/eodb-trade-license"/>
              </div>
              <div class="md:col-span-4">
                <input class="w-full bg-surface-container-lowest border border-outline px-3 py-2 font-headline text-xs text-primary focus:outline-none focus:ring-1 focus:ring-primary rounded-none" id="scraper-hint-input" placeholder="Task Hint: Commercial Bakery Health Trade License" type="text" value="Commercial Bakery Health Trade License"/>
              </div>
            </div>

            <div>
              <button class="bg-primary hover:bg-primary-container text-on-primary px-5 py-2.5 font-headline text-xs font-semibold tracking-wide flex items-center gap-1.5 transition-colors shadow-sm" id="btn-run-scraper">
                <span class="material-symbols-outlined text-[16px]">travel_explore</span>
                <span>Crawl Official Gateway &amp; Audit Code</span>
              </button>
            </div>

            <!-- Crawler Terminal Output -->
            <div class="mt-4">
              <div class="font-headline text-[11px] font-semibold text-secondary uppercase mb-1 flex items-center justify-between">
                <span>Ingestion Terminal Log (SHA-256 Validated)</span>
                <span class="font-code text-[10px]">READY</span>
              </div>
              <pre class="bg-primary text-primary-fixed p-4 font-code text-xs overflow-x-auto max-h-80 border border-primary-container leading-relaxed whitespace-pre-wrap" id="scraper-output">[IDLE] Ready to ingest portal content. Select a preset or input an official municipal government URL above.
Current Jurisdictional Profile: Municipal Corporation of Greater Mumbai (MCGM / BMC)
Statutory Framework: MMC Act 1888 § 394 &amp; Maharashtra Act LXI of 2017</pre>
            </div>
          </div>
        </div>

        <!-- Tab 5.2: Step Verification Queue -->
        <div class="admin-tab-pane space-y-4" id="pane-moderation" style="display:none;">
          <div class="bg-surface-container-lowest p-6 border border-outline-variant shadow-sm">
            <h3 class="font-headline text-sm font-semibold text-primary uppercase mb-2">Step Verification &amp; Fee Update Queue</h3>
            <p class="font-body text-xs text-on-surface-variant mb-4">
              Review and manually verify statutory steps across active dockets. Verified steps carry immutable administrative standing in citizen roadmaps.
            </p>
            <div class="space-y-3" id="moderation-queue-container">
              <!-- Rendered dynamically -->
            </div>
          </div>
        </div>

        <!-- Tab 5.3: Audit Trail -->
        <div class="admin-tab-pane space-y-4" id="pane-audit" style="display:none;">
          <div class="bg-surface-container-lowest p-6 border border-outline-variant shadow-sm">
            <h3 class="font-headline text-sm font-semibold text-primary uppercase mb-2">Cryptographic Statutory Audit Logs</h3>
            <p class="font-body text-xs text-on-surface-variant mb-4">
              Complete chronological audit trail of all verified updates, scraping runs, and regulatory adjustments.
            </p>
            <div class="space-y-2" id="audit-logs-container">
              <!-- Rendered dynamically -->
            </div>
          </div>
        </div>

        <!-- Tab 5.4: Citizen Feedback -->
        <div class="admin-tab-pane space-y-4" id="pane-feedback" style="display:none;">
          <div class="bg-surface-container-lowest p-6 border border-outline-variant shadow-sm">
            <h3 class="font-headline text-sm font-semibold text-primary uppercase mb-2">Citizen Discrepancy &amp; Counter Delay Reports</h3>
            <p class="font-body text-xs text-on-surface-variant mb-4">
              Citizen-reported discrepancies regarding unexpected fees, counter window closures, or altered document requirements.
            </p>
            <div class="space-y-2" id="feedback-reports-container">
              <!-- Rendered dynamically -->
            </div>
          </div>
        </div>

      </section>

    </div>
  </main>

  <!-- ======================================================================
       DRAWER: Step Detail Quick-Inspection Drawer
       ====================================================================== -->
  <div class="drawer-backdrop" id="drawer-backdrop"></div>
  <div class="step-drawer" id="step-drawer">
    <div class="p-6 h-full flex flex-col justify-between overflow-y-auto">
      <div>
        <div class="flex items-center justify-between pb-3 mb-4 border-b border-outline-variant">
          <div class="flex items-center gap-2">
            <span class="font-code text-xs font-bold bg-primary text-on-primary px-2 py-0.5" id="drawer-step-badge">Step 3</span>
            <span class="font-headline text-xs font-semibold text-emerald-800 bg-emerald-100 px-2 py-0.5" id="drawer-confidence">99% Match</span>
          </div>
          <button class="text-secondary hover:text-primary" id="btn-close-drawer">
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <h2 class="font-headline text-lg font-semibold text-primary mb-2" id="drawer-title">MFB Fire Safety Compliance &amp; Kitchen NOC</h2>
        <div class="font-code text-xs text-secondary mb-3" id="drawer-gazette-ref">Statutory Authority: Maharashtra Fire Act 2006 § 3(1)</div>
        <p class="font-body text-xs text-on-surface-variant mb-4 leading-relaxed" id="drawer-step-desc">
          Mandatory fire protection installation, Class-K commercial exhaust hood duct suppression, LPG pipeline safety valve certificate, and dual emergency escape audit.
        </p>

        <div class="space-y-3">
          <div class="bg-surface-container p-3 border border-outline-variant">
            <div class="font-headline text-[11px] font-semibold text-secondary uppercase mb-1">Administrative Agency</div>
            <div class="font-headline text-xs font-bold text-primary" id="drawer-dept-name">Mumbai Fire Brigade (Chief Fire Officer)</div>
            <div class="font-body text-xs text-on-surface-variant mt-0.5" id="drawer-office-addr">Byculla Fire Station Headquarters, Mumbai</div>
            <div class="font-code text-[11px] text-secondary mt-0.5" id="drawer-office-hours">Mon-Fri 10:30 AM - 3:30 PM IST</div>
          </div>

          <div class="bg-surface-container-low p-3 border border-outline-variant">
            <div class="font-headline text-[11px] font-semibold text-secondary uppercase mb-1">Processing Timeline &amp; Fees</div>
            <div class="flex justify-between font-headline text-xs mb-1">
              <span>SLA Target:</span>
              <strong class="font-code text-primary" id="drawer-sla-days">18 Days</strong>
            </div>
            <div class="text-xs space-y-0.5 text-secondary" id="drawer-fee-breakdown">
              Total: <strong>₹18,500.00</strong>
            </div>
          </div>

          <div>
            <div class="font-headline text-xs font-semibold text-primary uppercase mb-1">Prescribed Forms</div>
            <div class="space-y-1 text-xs" id="drawer-forms-list">
              <div class="bg-surface-container-lowest p-2 border border-outline-variant">• <strong>FORM A - MFB</strong>: Fire Safety Application</div>
            </div>
          </div>

          <div>
            <div class="font-headline text-xs font-semibold text-primary uppercase mb-1">Mandatory Documents</div>
            <div class="space-y-1 text-xs" id="drawer-docs-list">
              <div class="bg-surface-container-lowest p-2 border border-outline-variant">• <strong>Sealed Architectural Layout &amp; MEP Drawing</strong></div>
            </div>
          </div>
        </div>
      </div>

      <div class="pt-6 border-t border-outline-variant space-y-2 mt-6">
        <div class="flex gap-2">
          <button class="flex-1 bg-primary hover:bg-primary-container text-on-primary font-headline text-xs font-semibold py-2.5 px-3 flex items-center justify-center gap-1.5 transition-colors" id="btn-toggle-complete">
            <span class="material-symbols-outlined text-[16px]">check_circle</span>
            <span>Mark Step Completed</span>
          </button>
          <button class="bg-surface-container hover:bg-surface-container-high text-primary font-headline text-xs font-semibold py-2.5 px-3 border border-outline-variant flex items-center justify-center" onclick="window.app.inspectFullDossierFromDrawer()">
            <span>Full Dossier</span>
          </button>
        </div>
        <a class="block text-center font-code text-[11px] text-primary underline truncate pt-1" href="#" id="drawer-provenance-url" target="_blank">
          portal.mcgm.gov.in/eodb-fire-noc
        </a>
      </div>
    </div>
  </div>

  <!-- ======================================================================
       FOOTER: GIGW 3.0 / INDIAN GOVERNMENT COMPLIANT FOOTER
       ====================================================================== -->
  <footer class="w-full bg-surface-container border-t border-outline-variant mt-auto">
    <div class="max-w-[1200px] mx-auto px-4 md:px-8 py-8">
      
      <!-- Primary 3-Column Jurisdictional Disclosure -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pb-6 border-b border-outline-variant">
        <div class="space-y-1.5">
          <div class="font-headline text-xs text-primary font-bold uppercase tracking-wider">
            Jurisdictional Authority &amp; Government Standing
          </div>
          <p class="font-body text-xs text-on-surface-variant leading-relaxed">
            Maintained under the authority of Municipal Corporation of Greater Mumbai (MCGM / BMC) and Government of Maharashtra. Filings and administrative routes recorded through this portal establish binding procedural standing across municipal departments pursuant to the Mumbai Municipal Corporation Act (MMC Act 1888).
          </p>
        </div>
        
        <div class="space-y-1.5">
          <div class="font-headline text-xs text-primary font-bold uppercase tracking-wider">
            Right to Public Services &amp; Transparency
          </div>
          <p class="font-body text-xs text-on-surface-variant leading-relaxed">
            All statutory service level agreements (SLAs), prerequisite dependencies, fee schedules, and ledger entries conform to the Maharashtra Right to Public Services Act 2015. Certified receipt instruments carry SHA-256 verification hashes recognized by citizen grievance portals.
          </p>
        </div>

        <div class="space-y-1.5">
          <div class="font-headline text-xs text-primary font-bold uppercase tracking-wider">
            Ledger Provenance &amp; Node Status
          </div>
          <div class="bg-surface-container-lowest p-3 border border-outline-variant">
            <div class="font-headline text-[10px] text-outline font-semibold">VERIFICATION TIMESTAMP</div>
            <div class="font-code text-xs text-primary font-semibold">2024-10-24 16:42:09 IST [NODE MUM-W-HW]</div>
            <div class="font-headline text-[10px] text-outline font-semibold mt-1">HASH RECORD (SHA-256)</div>
            <div class="font-code text-[11px] text-secondary truncate">0x9f82c4...e18b42cd</div>
          </div>
        </div>
      </div>

      <!-- Government Compliance Bar (GIGW 3.0 / S3WaaS Guidelines) -->
      <div class="pt-4 flex flex-col md:flex-row items-center justify-between text-secondary font-headline text-xs gap-3">
        <div class="flex items-center gap-2 flex-wrap">
          <span>© Municipal Corporation of Greater Mumbai (MCGM). Public Health &amp; Fire Safety Division.</span>
          <span>•</span>
          <span>Form Docket CTN-2024-MUM</span>
          <span>•</span>
          <span class="text-emerald-800 font-semibold flex items-center gap-1">
            <span class="material-symbols-outlined text-[14px]">verified</span>
            Certified under GIGW 3.0 Standards
          </span>
        </div>
        
        <div class="flex items-center gap-4 flex-wrap">
          <a class="hover:text-primary transition-colors" href="https://services.india.gov.in" target="_blank">National Portal of India</a>
          <a class="hover:text-primary transition-colors" href="https://aaplesarkar.mahaonline.gov.in" target="_blank">Aaple Sarkar</a>
          <a class="hover:text-primary transition-colors" href="https://foscos.fssai.gov.in" target="_blank">FoSCoS (FSSAI)</a>
          <a class="hover:text-primary transition-colors" href="https://digilocker.gov.in" target="_blank">DigiLocker</a>
          <a class="hover:text-primary transition-colors" href="#">RTI Act &amp; Grievance Redressal</a>
          <a class="hover:text-primary transition-colors" href="#">Website Policies</a>
        </div>
      </div>

      <div class="pt-2 text-center text-outline text-[11px] font-body">
        Web Information Manager: Executive Health Officer, Municipal Corporation of Greater Mumbai | Last Reviewed &amp; Updated: 26 September 2026
      </div>

    </div>
  </footer>

  <!-- Scripts: Graph Visualizer, Admin Manager, Main Application -->
  <script src="/static/graph_view.js"></script>
  <script src="/static/admin_view.js"></script>
  <script src="/static/app.js"></script>
</body>
</html>
'''

with open('app/static/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("SUCCESS: index.html generated with Indian Government & Stitch design localization.")
