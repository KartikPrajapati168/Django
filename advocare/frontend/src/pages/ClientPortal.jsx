import React, { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import Chart from "chart.js/auto";

function ClientPortal() {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [cases, setCases] = useState([]);
  const [stats, setStats] = useState({
    totalCases: 0,
    activeCases: 0,
    pendingRequests: 0,
    completedCases: 0,
  });
  const [messages, setMessages] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState("dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedCase, setSelectedCase] = useState(null);
  const [showCreateCasePage, setShowCreateCasePage] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [selectedChat, setSelectedChat] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [uploadingDoc, setUploadingDoc] = useState(false);
  const [selectedDocCase, setSelectedDocCase] = useState(null);
  const [showDocModal, setShowDocModal] = useState(false);
  const [selectedDocType, setSelectedDocType] = useState("other");
  const [selectedFile, setSelectedFile] = useState(null);
  const [lawFirms, setLawFirms] = useState([]);
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [searchFilters, setSearchFilters] = useState({
    specialization: "",
    location: "",
    experience: "",
    rating: "",
    language: "",
  });
  const [showAISection, setShowAISection] = useState(false);
  const [aiCaseDesc, setAiCaseDesc] = useState("");
  const [aiRecommendations, setAiRecommendations] = useState([]);
  const [aiLoading, setAiLoading] = useState(false);
  const [createCaseError, setCreateCaseError] = useState("");
  const [createCaseSuccess, setCreateCaseSuccess] = useState("");
  const [submittingCase, setSubmittingCase] = useState(false);
  const [caseFiles, setCaseFiles] = useState({
    fir: null,
    notice: null,
    evidence: null,
    correspondence: null,
    other: null,
  });
  const [lawFirmsLoading, setLawFirmsLoading] = useState(false);

  // New states for Law Firm Detail Page
  const [selectedLawFirm, setSelectedLawFirm] = useState(null);
  const [showLawFirmDetail, setShowLawFirmDetail] = useState(false);

  // Profile edit mode
  const [profileEditMode, setProfileEditMode] = useState(false);
  const [editedProfile, setEditedProfile] = useState({
    name: "",
    email: "",
    phone: "",
    city: "",
  });

  // Assignment modal states
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedFirmForAssign, setSelectedFirmForAssign] = useState(null);
  const [selectedCaseToAssign, setSelectedCaseToAssign] = useState("");
  const [assigningCase, setAssigningCase] = useState(false);

  const [newCase, setNewCase] = useState({
    title: "",
    case_type: "",
    description: "",
    urgency: "normal",
    court_location: "",
    opposing_party: "",
    filing_deadline: "",
    estimated_value: "",
    previous_litigation: "no",
    previous_case_number: "",
    required_documents: "",
    witnesses: "",
    preferred_outcome: "",
    additional_notes: "",
  });

  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const messageInterval = useRef(null);
  const chatPollInterval = useRef(null);
  const chatEndRef = useRef(null);

  // const computeStats = (caseData) => ({
  //     totalCases: caseData.length,
  //     activeCases: caseData.filter((c) =>
  //         ["in_progress", "assigned", "in_court"].includes(c.status),
  //     ).length,
  //     pendingRequests: caseData.filter((c) => c.status === "pending").length,
  //     completedCases: caseData.filter((c) =>
  //         ["resolved", "closed", "completed"].includes(c.status),
  //     ).length,
  // });

  const computeStats = (caseData) => ({
    totalCases: caseData.length,
    activeCases: caseData.filter(
      (c) =>
        ["in_progress", "assigned", "in_court"].includes(c.status) &&
        (c.law_firm_id || c.law_firm),
    ).length,
    pendingRequests: caseData.filter((c) => c.status === "pending").length,
    completedCases: caseData.filter((c) =>
      ["resolved", "closed", "completed"].includes(c.status),
    ).length,
  });

  const tryEndpoints = async (endpoints) => {
    for (const ep of endpoints) {
      try {
        const r = await API.get(ep);
        const data = Array.isArray(r.data)
          ? r.data
          : r.data?.results || r.data?.data || [];
        return data;
      } catch (err) {
        console.warn(`Endpoint ${ep} failed:`, err?.response?.status);
      }
    }
    return [];
  };

  // const loadCases = useCallback(async () => {
  //     try {
  //         const res = await API.get("/cases/my-cases/");
  //         const caseList = res.data.data || [];
  //         setCases(caseList);
  //         setStats(computeStats(caseList));
  //         return caseList;
  //     } catch (err) {
  //         console.error("Load cases failed", err);
  //         return [];
  //     }
  // }, []);

  const loadCases = useCallback(async () => {
    try {
      const res = await API.get("/cases/my-cases/");
      let caseList = res.data.data || [];
      // Remove any case that looks like an onboarding placeholder
      caseList = caseList.filter(
        (c) => !c.title?.toLowerCase().includes("onboarding"),
      );
      setCases(caseList);
      setStats(computeStats(caseList));
      return caseList;
    } catch (err) {
      console.error("Load cases failed", err);
      return [];
    }
  }, []);

  const loadLawFirms = useCallback(async () => {
    setLawFirmsLoading(true);
    try {
      const res = await API.get("/profiles/lawfirms/");
      setLawFirms(res.data);
    } catch (err) {
      console.error("Load law firms failed", err);
      setLawFirms([]);
    } finally {
      setLawFirmsLoading(false);
    }
  }, []);

  const loadUserProfile = async () => {
    try {
      const res = await API.get("/profiles/auth/me/");
      setUserData(res.data);
      setEditedProfile({
        name: res.data.name || "",
        email: res.data.email || "",
        phone: res.data.phone || "",
        city: res.data.city || "",
      });
    } catch (err) {
      console.error("Profile load failed", err);
    }
  };

  const updateClientProfile = async (updatedData) => {
    try {
      await API.patch("/profiles/client-profile/update/", updatedData);
      await loadUserProfile();
      alert("Profile updated successfully");
      setProfileEditMode(false);
    } catch (err) {
      console.error("Update failed", err);
      alert("Update failed: " + (err.response?.data?.detail || err.message));
    }
  };

  useEffect(() => {
    let isMounted = true;
    const loadDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          navigate("/");
          return;
        }

        let profileData = null;
        const profileEndpoints = [
          "profiles/client-dashboard/",
          "profiles/me/",
          "profiles/client-profile/",
          "auth/me/",
          "users/me/",
        ];
        for (const ep of profileEndpoints) {
          try {
            const r = await API.get(ep);
            profileData = r.data;
            console.log("Profile loaded from:", ep, profileData);
            break;
          } catch (err) {
            console.warn("Profile endpoint failed:", ep);
          }
        }

        if (!isMounted) return;

        if (!profileData) {
          setUserData({ name: "Client", email: "", status: "approved" });
          setApiError("Could not load profile. Showing limited data.");
        } else {
          const status =
            profileData.status || profileData.approval_status || "approved";
          if (status === "pending") {
            navigate("/pending-onboarding");
            return;
          }
          if (status === "rejected") {
            navigate("/client-onboarding");
            return;
          }
          setUserData(profileData);
          setEditedProfile({
            name: profileData.name || "",
            email: profileData.email || "",
            phone: profileData.phone || "",
            city: profileData.city || "",
          });
          setApiError(null);
        }

        await loadCases();

        const msgData = await tryEndpoints([
          "messages/my-messages/",
          "messages/",
          "api/messages/",
        ]);
        if (isMounted) setMessages(msgData);

        const notifData = await tryEndpoints([
          "notifications/my-notifications/",
          "notifications/",
          "api/notifications/",
        ]);
        if (isMounted) setNotifications(notifData);

        await loadLawFirms();
      } catch (error) {
        console.error("Dashboard error:", error);
        if (!isMounted) return;
        if (error.response?.status === 401) {
          localStorage.clear();
          navigate("/");
        } else
          setApiError(
            "Some data failed to load. " + (error.response?.data?.detail || ""),
          );
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    loadDashboard();

    messageInterval.current = setInterval(async () => {
      try {
        const msgData = await tryEndpoints([
          "messages/my-messages/",
          "messages/",
        ]);
        setMessages(msgData);
      } catch {}
    }, 8000);

    return () => {
      isMounted = false;
      if (messageInterval.current) clearInterval(messageInterval.current);
      if (chatPollInterval.current) clearInterval(chatPollInterval.current);
    };
  }, [navigate, loadCases, loadLawFirms]);

  // Chat polling
  useEffect(() => {
    if (chatPollInterval.current) clearInterval(chatPollInterval.current);
    if (selectedChat && activeView === "messages") {
      chatPollInterval.current = setInterval(() => {
        loadChatMessages(selectedChat.caseId, selectedChat.firmId);
      }, 3000);
    }
    return () => {
      if (chatPollInterval.current) clearInterval(chatPollInterval.current);
    };
  }, [selectedChat, activeView]);

  useEffect(() => {
    if (chatEndRef.current)
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  useEffect(() => {
    if (activeView !== "dashboard") return;
    const timer = setTimeout(() => {
      if (chartRef.current) initChart();
    }, 300);
    return () => {
      clearTimeout(timer);
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
        chartInstanceRef.current = null;
      }
    };
  }, [activeView, cases]);

  const initChart = () => {
    if (!chartRef.current) return;
    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy();
      chartInstanceRef.current = null;
    }
    const ctx = chartRef.current.getContext("2d");
    if (!ctx) return;
    const p = cases.filter((c) => c.status === "pending").length;
    const a = cases.filter((c) => c.status === "assigned").length;
    const ip = cases.filter((c) =>
      ["in_progress", "in_court"].includes(c.status),
    ).length;
    const c = cases.filter((c) =>
      ["resolved", "closed", "completed"].includes(c.status),
    ).length;
    const hasData = p + a + ip + c > 0;
    chartInstanceRef.current = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Pending", "Assigned", "In Progress", "Completed"],
        datasets: [
          {
            data: hasData ? [p || 0, a || 0, ip || 0, c || 0] : [1, 1, 1, 1],
            backgroundColor: ["#ffc107", "#17a2b8", "#2d5bb5", "#28a745"],
            borderWidth: 2,
            borderColor: "#fff",
            hoverOffset: 15,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: { padding: 20, usePointStyle: true },
          },
          tooltip: {
            callbacks: {
              label: (ctx) =>
                hasData
                  ? `${ctx.label}: ${ctx.raw} case(s)`
                  : `${ctx.label}: No data yet`,
            },
          },
        },
      },
    });
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
  };

  // ======================= AI MATCHING ALGORITHM =======================
  // Extracts legal keywords from description and matches against law firm specializations
  const matchLawFirmsByDescription = (description, firms) => {
    if (!description || firms.length === 0) return [];

    // Define legal specialization keywords mapping
    const specializationKeywords = {
      criminal: [
        "criminal",
        "assault",
        "theft",
        "robbery",
        "murder",
        "dowry",
        "cheating",
        "fraud",
        "bail",
        "anticipatory",
        "criminal intimidation",
        "physical assault",
        "attack",
        "injury",
        "police",
        "fir",
        "complaint",
        "offence",
        "penal code",
      ],
      civil: [
        "civil",
        "property dispute",
        "contract",
        "breach",
        "landlord",
        "tenant",
        "eviction",
        "possession",
        "injunction",
        "specific performance",
        "recovery",
        "debt",
        "money suit",
      ],
      family: [
        "family",
        "divorce",
        "maintenance",
        "custody",
        "child support",
        "alimony",
        "matrimonial",
        "domestic violence",
        "inheritance",
        "succession",
        "will",
        "guardianship",
      ],
      corporate: [
        "corporate",
        "company",
        "shareholder",
        "director",
        "merger",
        "acquisition",
        "insolvency",
        "bankruptcy",
        "securities",
        "stock market",
        "business",
        "commercial",
        "partnership",
      ],
      property: [
        "property",
        "real estate",
        "land",
        "title",
        "possession",
        "lease",
        "rent agreement",
        "builder",
        "construction",
        "flats",
        "apartment",
        "sale deed",
        "gift deed",
      ],
      tax: [
        "tax",
        "income tax",
        "gst",
        "goods and services tax",
        "customs",
        "excise",
        "vat",
        "assessment",
        "notice",
        "appeal",
        "tribunal",
        "tax evasion",
      ],
      employment: [
        "employment",
        "labour",
        "service",
        "termination",
        "wrongful dismissal",
        "harassment",
        "workplace",
        "salary",
        "wages",
        "bonus",
        "provident fund",
        "esi",
      ],
      matrimonial: [
        "matrimonial",
        "marriage",
        "divorce",
        "annulment",
        "restitution",
        "conjugal",
        "cruelty",
        "dowry",
        "maintenance",
        "child custody",
      ],
      consumer: [
        "consumer",
        "defective product",
        "deficiency in service",
        "refund",
        "compensation",
        "consumer court",
        "consumer forum",
        "online purchase",
        "flipkart",
        "amazon",
        "repair",
      ],
      cyber: [
        "cyber",
        "online",
        "internet",
        "hacking",
        "phishing",
        "identity theft",
        "data breach",
        "privacy",
        "social media",
        "facebook",
        "whatsapp",
        "digital",
        "computer",
      ],
      constitutional: [
        "constitution",
        "fundamental rights",
        "writ",
        "public interest litigation",
        "pil",
        "high court",
        "supreme court",
        "statutory",
        "legal validity",
      ],
      arbitration: [
        "arbitration",
        "mediation",
        "conciliation",
        "alternative dispute resolution",
        "adr",
        "arbitral",
        "award",
      ],
    };

    // Normalize description: lowercase, remove punctuation
    const descLower = description.toLowerCase();
    const words = descLower.split(/\s+/);

    // Count keyword matches per specialization
    const scores = {};
    for (const [spec, keywords] of Object.entries(specializationKeywords)) {
      let matchCount = 0;
      for (const kw of keywords) {
        if (descLower.includes(kw)) {
          matchCount++;
        }
      }
      // Also check individual words (for short keywords)
      for (const word of words) {
        if (
          keywords.some(
            (kw) => kw === word || word.includes(kw) || kw.includes(word),
          )
        ) {
          matchCount += 0.5;
        }
      }
      scores[spec] = matchCount;
    }

    // Find top matching specializations
    const sortedSpecs = Object.entries(scores).sort((a, b) => b[1] - a[1]);
    const primarySpec = sortedSpecs[0]?.[0] || "general";
    const secondarySpec = sortedSpecs[1]?.[0] || "";

    // Calculate match percentage for each firm
    const matched = firms.map((firm) => {
      const firmSpec = (
        firm.specialization ||
        firm.practice_areas ||
        ""
      ).toLowerCase();
      let matchScore = 0;
      // Direct match with primary spec
      if (firmSpec.includes(primarySpec)) matchScore += 60;
      // Check secondary spec
      if (secondarySpec && firmSpec.includes(secondarySpec)) matchScore += 30;
      // Check for any keyword overlap
      for (const [spec, keywords] of Object.entries(specializationKeywords)) {
        if (firmSpec.includes(spec)) {
          const kwMatches = keywords.filter((kw) =>
            descLower.includes(kw),
          ).length;
          matchScore += Math.min(kwMatches * 5, 40);
        }
      }
      // Additional weight for experience (5+ years adds up to 10)
      const exp = parseInt(firm.experience || firm.years_of_experience || 0);
      if (exp >= 10) matchScore += 10;
      else if (exp >= 5) matchScore += 5;

      // Cap at 100
      const matchPercent = Math.min(Math.round(matchScore), 100);
      return {
        ...firm,
        match_percentage: matchPercent,
        ai_accuracy: Math.min(95, 70 + Math.floor(matchPercent / 3)),
        success_rate:
          firm.success_rate || `${70 + Math.floor(matchPercent / 4)}%`,
      };
    });

    // Sort by match percentage descending
    matched.sort((a, b) => b.match_percentage - a.match_percentage);
    return matched.slice(0, 6);
  };

  const getAIRecommendations = async () => {
    if (!aiCaseDesc.trim()) return;
    setAiLoading(true);
    setAiRecommendations([]);
    try {
      // Try backend AI endpoint first
      const endpoints = [
        "/recommendations/ai-match/",
        "/ai/match/",
        "/api/recommendations/ai-match/",
      ];
      let recs = [];
      for (const ep of endpoints) {
        try {
          const r = await API.post(ep, { description: aiCaseDesc });
          recs = (r.data?.results || r.data || []).slice(0, 6);
          if (recs.length > 0) break;
        } catch {}
      }
      if (recs.length === 0 && lawFirms.length > 0) {
        // Fallback to frontend matching algorithm
        recs = matchLawFirmsByDescription(aiCaseDesc, lawFirms);
      }
      setAiRecommendations(recs);
    } catch (e) {
      console.error("AI matching error", e);
      // Use frontend matching as final fallback
      const recs = matchLawFirmsByDescription(aiCaseDesc, lawFirms);
      setAiRecommendations(recs);
    } finally {
      setAiLoading(false);
    }
  };

  // ======================= END AI MATCHING =======================

  const handleCreateCase = async (e) => {
    e.preventDefault();
    setSubmittingCase(true);
    setCreateCaseError("");
    setCreateCaseSuccess("");

    const payload = {};
    Object.keys(newCase).forEach((k) => {
      if (newCase[k] !== "" && newCase[k] !== null) payload[k] = newCase[k];
    });
    payload.status = "pending";

    let caseId = null;
    const caseEndpoints = [
      "cases/create/",
      "cases/",
      "api/cases/create/",
      "api/cases/",
    ];

    for (const ep of caseEndpoints) {
      try {
        const r = await API.post(ep, payload);
        caseId = r.data?.id || r.data?.case_id || r.data?.pk;
        console.log("Case created at:", ep, "ID:", caseId);
        break;
      } catch (err) {
        console.warn(
          "Case create failed at:",
          ep,
          err?.response?.status,
          err?.response?.data,
        );
        if (err?.response?.status === 400) {
          const errData = err?.response?.data;
          const errMsg =
            typeof errData === "object"
              ? JSON.stringify(errData)
              : String(errData);
          setCreateCaseError(`Validation error: ${errMsg}`);
          setSubmittingCase(false);
          return;
        }
      }
    }

    if (!caseId && !createCaseError) {
      for (const ep of caseEndpoints) {
        try {
          const fd = new FormData();
          Object.keys(payload).forEach((k) => fd.append(k, payload[k]));
          const r = await API.post(ep, fd, {
            headers: { "Content-Type": "multipart/form-data" },
          });
          caseId = r.data?.id || r.data?.case_id || r.data?.pk;
          console.log("Case created via FormData at:", ep, "ID:", caseId);
          break;
        } catch (err) {
          console.warn("FormData create failed:", ep);
        }
      }
    }

    if (!caseId && !createCaseError) {
      setCreateCaseError(
        "Could not create case. Please check your backend API endpoints.",
      );
      setSubmittingCase(false);
      return;
    }

    if (caseId) {
      for (const [docType, file] of Object.entries(caseFiles)) {
        if (!file) continue;
        try {
          const fd = new FormData();
          fd.append("file", file);
          fd.append("doc_type", docType);
          fd.append("case_id", caseId);
          const docEndpoints = [
            "documents/upload/",
            "cases/documents/upload/",
            "api/documents/upload/",
          ];
          let uploaded = false;
          for (const dep of docEndpoints) {
            try {
              await API.post(dep, fd, {
                headers: { "Content-Type": "multipart/form-data" },
              });
              uploaded = true;
              break;
            } catch (err) {
              console.warn(`Doc upload failed to ${dep}:`, err);
            }
          }
          if (!uploaded) console.warn(`Document ${docType} not uploaded`);
        } catch (de) {
          console.warn("Doc upload failed:", docType, de);
        }
      }
    }

    setCreateCaseSuccess("Case created successfully! Redirecting...");
    await loadCases();
    setTimeout(() => {
      setShowCreateCasePage(false);
      setCreateCaseSuccess("");
      setNewCase({
        title: "",
        case_type: "",
        description: "",
        urgency: "normal",
        court_location: "",
        opposing_party: "",
        filing_deadline: "",
        estimated_value: "",
        previous_litigation: "no",
        previous_case_number: "",
        required_documents: "",
        witnesses: "",
        preferred_outcome: "",
        additional_notes: "",
      });
      setCaseFiles({
        fir: null,
        notice: null,
        evidence: null,
        correspondence: null,
        other: null,
      });
      setActiveView("my-cases");
    }, 1800);
    setSubmittingCase(false);
  };

  const viewCaseDetails = (c) => {
    setSelectedCase(c);
    setActiveView("case-detail");
  };

  const viewLawFirmDetails = (firm) => {
    setSelectedLawFirm(firm);
    setShowLawFirmDetail(true);
    setActiveView("lawfirm-detail");
  };

  const openChat = (caseItem, firm) => {
    setSelectedChat({
      caseId: caseItem.id,
      firmName: firm?.firm_name || firm?.name || "Law Firm",
      firmId: firm?.id,
    });
    loadChatMessages(caseItem.id, firm?.id);
    setActiveView("messages");
  };

  const loadChatMessages = async (caseId, firmId) => {
    try {
      const res = await API.get(`/chat/${caseId}/${firmId}/`);
      setChatMessages(res.data);
    } catch (err) {
      console.warn("Failed to load chat messages", err);
      setChatMessages([]);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedChat) return;
    const msg = newMessage;
    setNewMessage("");
    const payload = {
      case_id: selectedChat.caseId,
      receiver_id: selectedChat.firmId,
      content: msg,
    };
    try {
      await API.post("/chat/send/", payload);
      await loadChatMessages(selectedChat.caseId, selectedChat.firmId);
      const msgData = await tryEndpoints(["/chat/conversations/"]);
      setMessages(msgData);
    } catch (err) {
      console.error("Send message failed", err);
      alert("Failed to send message. Check console.");
      setNewMessage(msg);
    }
  };

  const uploadDocument = async () => {
    if (!selectedFile || !selectedDocCase) return;
    if (selectedFile.size > 10 * 1024 * 1024) {
      alert("File size exceeds 10MB limit");
      return;
    }
    setUploadingDoc(true);

    const fd = new FormData();
    fd.append("file", selectedFile);
    fd.append("doc_type", selectedDocType);
    fd.append("case_id", selectedDocCase.id);

    // Try multiple endpoints
    const endpoints = [
      "/documents/upload/",
      "/cases/documents/upload/",
      "/api/documents/upload/",
    ];
    let success = false;
    let errorMsg = "";

    for (const ep of endpoints) {
      try {
        await API.post(ep, fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        success = true;
        break;
      } catch (err) {
        errorMsg = err.response?.data?.detail || err.message;
        console.warn(`Upload to ${ep} failed:`, errorMsg);
      }
    }

    setUploadingDoc(false);
    if (success) {
      alert("Document uploaded successfully!");
      setShowDocModal(false);
      setSelectedFile(null);
      await loadCases(); // refresh to get updated documents list
    } else {
      alert(`Upload failed. ${errorMsg || "Check backend logs."}`);
    }
  };

  const assignCaseToFirm = async () => {
    if (!selectedFirmForAssign || !selectedCaseToAssign) return;
    setAssigningCase(true);
    try {
      await API.post(`/cases/${selectedCaseToAssign}/assign/`, {
        law_firm_id: selectedFirmForAssign.id,
      });
      alert("Case assigned successfully!");
      setShowAssignModal(false);
      await loadCases();
    } catch (err) {
      console.error("Assign failed", err);
      alert("Assignment failed. Check endpoint.");
    } finally {
      setAssigningCase(false);
    }
  };

  const filterLawFirms = () => {
    let f = lawFirms;
    if (searchFilters.specialization)
      f = f.filter((x) =>
        (x.specialization || x.practice_areas || "")
          .toLowerCase()
          .includes(searchFilters.specialization.toLowerCase()),
      );
    if (searchFilters.location)
      f = f.filter(
        (x) =>
          (x.city || x.location || "")
            .toLowerCase()
            .includes(searchFilters.location.toLowerCase()) ||
          (x.state || "")
            .toLowerCase()
            .includes(searchFilters.location.toLowerCase()),
      );
    if (searchFilters.experience)
      f = f.filter(
        (x) =>
          parseInt(x.experience || x.years_of_experience || 0) >=
          parseInt(searchFilters.experience),
      );
    if (searchFilters.rating)
      f = f.filter(
        (x) =>
          parseFloat(x.rating || x.average_rating || 0) >=
          parseFloat(searchFilters.rating),
      );
    if (searchFilters.language)
      f = f.filter((x) =>
        (x.languages || "")
          .toLowerCase()
          .includes(searchFilters.language.toLowerCase()),
      );
    return f;
  };

  const formatDate = (d) => {
    if (!d) return "N/A";
    try {
      return new Date(d).toLocaleDateString("en-IN", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return "N/A";
    }
  };

  const getStatusBadgeClass = (s) =>
    ({
      pending: "status-pending",
      assigned: "status-assigned",
      in_progress: "status-in-court",
      in_court: "status-in-court",
      resolved: "status-closed",
      closed: "status-closed",
      completed: "status-closed",
    })[s] || "status-pending";

  const getStatusText = (s) =>
    ({
      pending: "Pending",
      assigned: "Assigned",
      in_progress: "In Progress",
      in_court: "In Court",
      resolved: "Resolved",
      closed: "Closed",
      completed: "Completed",
    })[s] || (s ? s.charAt(0).toUpperCase() + s.slice(1) : "Unknown");

  const getFirmName = (firm) =>
    firm?.firm_name || firm?.name || firm?.law_firm_name || "Law Firm";
  const getFirmSpec = (firm) =>
    firm?.specialization || firm?.practice_areas || "General Practice";
  const getFirmLocation = (firm) =>
    [firm?.city, firm?.state].filter(Boolean).join(", ") ||
    firm?.location ||
    "Location N/A";

  const openAssignModal = (firm) => {
    const pendingCasesList = cases.filter((c) => c.status === "pending");
    if (pendingCasesList.length === 0) {
      alert("You have no pending cases. Please create a case first.");
      return;
    }
    setSelectedFirmForAssign(firm);
    setSelectedCaseToAssign(pendingCasesList[0]?.id || "");
    setShowAssignModal(true);
  };

  if (loading)
    return (
      <div className="pending-container">
        <div className="pending-card">
          <div className="spinner"></div>
          <h2>Loading Dashboard...</h2>
          <p style={{ color: "#6c757d", marginTop: "10px" }}>
            Connecting to server...
          </p>
        </div>
      </div>
    );

  const unreadCount = messages.filter((m) => !m.is_read).length;
  const unreadNotif = notifications.filter((n) => !n.is_read).length;

  // CREATE CASE PAGE
  if (showCreateCasePage) {
    return (
      <div className="client-portal-container">
        <div className="container-fluid">
          <div className={`sidebar ${sidebarCollapsed ? "collapsed" : ""}`}>
            <div className="logo">
              <div className="logo-icon">
                <i className="fas fa-balance-scale"></i>
              </div>
              <div className="logo-text">Advocare</div>
            </div>
            <div className="sidebar-nav">
              <button
                className="sidebar-item"
                onClick={() => {
                  setShowCreateCasePage(false);
                  setActiveView("dashboard");
                }}
              >
                <div className="sidebar-icon">
                  <i className="fas fa-arrow-left"></i>
                </div>
                <div className="nav-text">Back to Dashboard</div>
              </button>
            </div>
            <div className="user-profile">
              <div className="user-avatar">
                {userData?.name?.charAt(0)?.toUpperCase() || "C"}
              </div>
              <div className="user-info">
                <h4>{userData?.name || "Client"}</h4>
                <p>Client Portal</p>
              </div>
            </div>
          </div>

          <div className="main-content">
            <div className="header">
              <div className="d-flex align-items-center">
                <div
                  className="sidebar-toggle"
                  onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                >
                  <i className="fas fa-bars"></i>
                </div>
                <div className="page-title">
                  <i className="fas fa-plus-circle"></i>
                  <span>Create New Case</span>
                </div>
              </div>
              <button className="btn-outline" onClick={handleLogout}>
                <i className="fas fa-sign-out-alt"></i> Logout
              </button>
            </div>

            {createCaseError && (
              <div
                style={{
                  background: "#f8d7da",
                  color: "#721c24",
                  padding: "12px 20px",
                  borderRadius: "8px",
                  marginBottom: "20px",
                  borderLeft: "4px solid #dc3545",
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "10px",
                }}
              >
                <i
                  className="fas fa-exclamation-circle"
                  style={{ marginTop: "2px" }}
                ></i>
                <div style={{ flex: 1 }}>
                  <strong>Error:</strong> {createCaseError}
                </div>
                <button
                  onClick={() => setCreateCaseError("")}
                  style={{
                    marginLeft: "auto",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: "#721c24",
                    fontSize: "18px",
                    padding: 0,
                  }}
                >
                  &times;
                </button>
              </div>
            )}
            {createCaseSuccess && (
              <div
                style={{
                  background: "#d4edda",
                  color: "#155724",
                  padding: "12px 20px",
                  borderRadius: "8px",
                  marginBottom: "20px",
                  borderLeft: "4px solid #28a745",
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                }}
              >
                <i className="fas fa-check-circle"></i>
                <span>{createCaseSuccess}</span>
              </div>
            )}

            <form onSubmit={handleCreateCase}>
              {/* Case creation form - same as original, omitted for brevity but should remain unchanged */}
              <div className="content-card mb-4">
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    marginBottom: "20px",
                    paddingBottom: "15px",
                    borderBottom: "2px solid var(--secondary)",
                  }}
                >
                  <div
                    style={{
                      width: "36px",
                      height: "36px",
                      borderRadius: "50%",
                      background: "var(--primary)",
                      color: "white",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: "700",
                      flexShrink: 0,
                    }}
                  >
                    1
                  </div>
                  <h4
                    style={{
                      margin: 0,
                      color: "var(--primary)",
                      fontSize: "20px",
                    }}
                  >
                    <i
                      className="fas fa-info-circle me-2"
                      style={{ color: "var(--secondary)" }}
                    ></i>
                    Basic Case Information
                  </h4>
                </div>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "20px",
                    marginBottom: "15px",
                  }}
                >
                  <div className="form-group">
                    <label className="fw-bold">
                      Case Type <span style={{ color: "red" }}>*</span>
                    </label>
                    <select
                      className="form-control"
                      value={newCase.case_type}
                      onChange={(e) =>
                        setNewCase({ ...newCase, case_type: e.target.value })
                      }
                      required
                    >
                      <option value="">Select case type</option>
                      {[
                        "criminal",
                        "civil",
                        "family",
                        "corporate",
                        "property",
                        "tax",
                        "employment",
                        "matrimonial",
                        "consumer",
                        "cyber",
                        "other",
                      ].map((t) => (
                        <option key={t} value={t}>
                          {t.charAt(0).toUpperCase() + t.slice(1)} Law
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="fw-bold">
                      Case Title <span style={{ color: "red" }}>*</span>
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      value={newCase.title}
                      onChange={(e) =>
                        setNewCase({ ...newCase, title: e.target.value })
                      }
                      required
                      placeholder="e.g., Property Dispute with Neighbor"
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label className="fw-bold">
                    Case Description <span style={{ color: "red" }}>*</span>
                  </label>
                  <textarea
                    className="form-control"
                    rows="5"
                    value={newCase.description}
                    onChange={(e) =>
                      setNewCase({ ...newCase, description: e.target.value })
                    }
                    required
                    placeholder="Describe your case in detail..."
                    style={{ resize: "vertical" }}
                  />
                </div>
              </div>
              {/* Additional sections for case details and documents - keep as original */}
              <div className="content-card mb-4">
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    marginBottom: "20px",
                    paddingBottom: "15px",
                    borderBottom: "2px solid var(--secondary)",
                  }}
                >
                  <div
                    style={{
                      width: "36px",
                      height: "36px",
                      borderRadius: "50%",
                      background: "var(--primary)",
                      color: "white",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: "700",
                      flexShrink: 0,
                    }}
                  >
                    2
                  </div>
                  <h4
                    style={{
                      margin: 0,
                      color: "var(--primary)",
                      fontSize: "20px",
                    }}
                  >
                    <i
                      className="fas fa-gavel me-2"
                      style={{ color: "var(--secondary)" }}
                    ></i>
                    Case Details
                  </h4>
                </div>
                <div className="form-group mb-3">
                  <label className="fw-bold">Case Urgency</label>
                  <div
                    style={{
                      display: "flex",
                      gap: "15px",
                      flexWrap: "wrap",
                      marginTop: "10px",
                    }}
                  >
                    {[
                      ["normal", "Normal (within 30 days)", "#28a745"],
                      ["high", "High (within 7 days)", "#ffc107"],
                      ["urgent", "Urgent (24-48 hours)", "#dc3545"],
                    ].map(([val, label, color]) => (
                      <label
                        key={val}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "8px",
                          cursor: "pointer",
                          padding: "8px 16px",
                          borderRadius: "8px",
                          border: `2px solid ${newCase.urgency === val ? color : "#e9ecef"}`,
                          background:
                            newCase.urgency === val ? `${color}20` : "white",
                        }}
                      >
                        <input
                          type="radio"
                          name="urgency"
                          value={val}
                          checked={newCase.urgency === val}
                          onChange={(e) =>
                            setNewCase({ ...newCase, urgency: e.target.value })
                          }
                          style={{ accentColor: color }}
                        />
                        <span
                          style={{
                            color: newCase.urgency === val ? color : "#333",
                            fontWeight: newCase.urgency === val ? "600" : "400",
                            fontSize: "14px",
                          }}
                        >
                          {label}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "20px",
                    marginBottom: "15px",
                  }}
                >
                  <div className="form-group">
                    <label className="fw-bold">
                      Preferred Court / Location
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      value={newCase.court_location}
                      onChange={(e) =>
                        setNewCase({
                          ...newCase,
                          court_location: e.target.value,
                        })
                      }
                      placeholder="e.g., Delhi High Court"
                    />
                  </div>
                  <div className="form-group">
                    <label className="fw-bold">Opposing Party (if any)</label>
                    <input
                      type="text"
                      className="form-control"
                      value={newCase.opposing_party}
                      onChange={(e) =>
                        setNewCase({
                          ...newCase,
                          opposing_party: e.target.value,
                        })
                      }
                      placeholder="Name of person/company"
                    />
                  </div>
                </div>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "20px",
                    marginBottom: "15px",
                  }}
                >
                  <div className="form-group">
                    <label className="fw-bold">Filing Deadline</label>
                    <input
                      type="date"
                      className="form-control"
                      value={newCase.filing_deadline}
                      onChange={(e) =>
                        setNewCase({
                          ...newCase,
                          filing_deadline: e.target.value,
                        })
                      }
                    />
                  </div>
                </div>
              </div>
              <div className="content-card mb-4">
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    marginBottom: "20px",
                    paddingBottom: "15px",
                    borderBottom: "2px solid var(--secondary)",
                  }}
                >
                  <div
                    style={{
                      width: "36px",
                      height: "36px",
                      borderRadius: "50%",
                      background: "var(--primary)",
                      color: "white",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: "700",
                      flexShrink: 0,
                    }}
                  >
                    3
                  </div>
                  <h4
                    style={{
                      margin: 0,
                      color: "var(--primary)",
                      fontSize: "20px",
                    }}
                  >
                    <i
                      className="fas fa-file-upload me-2"
                      style={{ color: "var(--secondary)" }}
                    ></i>
                    Case Documents
                  </h4>
                </div>
                <div
                  style={{
                    background: "#ebf8ff",
                    borderLeft: "4px solid #17a2b8",
                    padding: "12px 16px",
                    borderRadius: "8px",
                    marginBottom: "20px",
                    fontSize: "14px",
                  }}
                >
                  <i className="fas fa-info-circle me-2"></i>
                  <strong>Tip:</strong> Upload FIR / Notice / Agreement as
                  primary document. All documents are optional but strengthen
                  your case.
                </div>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fill, minmax(220px,1fr))",
                    gap: "16px",
                  }}
                >
                  {[
                    {
                      key: "fir",
                      icon: "fas fa-file-alt",
                      label: "FIR Document",
                      hint: "First Information Report",
                    },
                    {
                      key: "notice",
                      icon: "fas fa-file-contract",
                      label: "Notice / Agreement",
                      hint: "Legal notice or contract",
                    },
                    {
                      key: "evidence",
                      icon: "fas fa-images",
                      label: "Evidence",
                      hint: "Photos, screenshots, proof",
                    },
                    {
                      key: "correspondence",
                      icon: "fas fa-envelope",
                      label: "Correspondence",
                      hint: "Emails, letters, chats",
                    },
                    {
                      key: "other",
                      icon: "fas fa-folder",
                      label: "Other Documents",
                      hint: "Any other relevant docs",
                    },
                  ].map(({ key, icon, label, hint }) => (
                    <div
                      key={key}
                      onClick={() =>
                        document.getElementById(`cf-${key}`).click()
                      }
                      style={{
                        border: `2px dashed ${caseFiles[key] ? "#28a745" : "#dee2e6"}`,
                        borderRadius: "12px",
                        padding: "18px",
                        textAlign: "center",
                        cursor: "pointer",
                        background: caseFiles[key] ? "#f0fff4" : "white",
                      }}
                    >
                      <input
                        type="file"
                        id={`cf-${key}`}
                        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                        style={{ display: "none" }}
                        onChange={(e) => {
                          if (e.target.files[0])
                            setCaseFiles((p) => ({
                              ...p,
                              [key]: e.target.files[0],
                            }));
                        }}
                      />
                      <i
                        className={`${icon} fa-2x`}
                        style={{
                          color: caseFiles[key]
                            ? "#28a745"
                            : "var(--secondary)",
                          display: "block",
                          marginBottom: "8px",
                        }}
                      ></i>
                      <div
                        style={{
                          fontWeight: "600",
                          fontSize: "14px",
                          marginBottom: "4px",
                        }}
                      >
                        {label}
                      </div>
                      <div
                        style={{
                          fontSize: "12px",
                          color: "#6c757d",
                          marginBottom: "8px",
                        }}
                      >
                        {hint}
                      </div>
                      {caseFiles[key] ? (
                        <div
                          style={{
                            background: "#d4edda",
                            color: "#155724",
                            padding: "4px 10px",
                            borderRadius: "6px",
                            fontSize: "11px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "4px",
                          }}
                        >
                          <i className="fas fa-check-circle"></i>
                          <span
                            style={{
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                              maxWidth: "110px",
                            }}
                          >
                            {caseFiles[key].name}
                          </span>
                          <button
                            type="button"
                            onClick={(ev) => {
                              ev.stopPropagation();
                              setCaseFiles((p) => ({ ...p, [key]: null }));
                              document.getElementById(`cf-${key}`).value = "";
                            }}
                            style={{
                              background: "none",
                              border: "none",
                              color: "#dc3545",
                              cursor: "pointer",
                              fontWeight: "bold",
                            }}
                          >
                            ×
                          </button>
                        </div>
                      ) : (
                        <div style={{ color: "#adb5bd", fontSize: "12px" }}>
                          <i className="fas fa-cloud-upload-alt me-1"></i>Click
                          to upload
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "15px",
                  marginBottom: "40px",
                }}
              >
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateCasePage(false);
                    setCreateCaseError("");
                  }}
                  style={{
                    padding: "12px 30px",
                    borderRadius: "8px",
                    border: "none",
                    cursor: "pointer",
                    background: "#6c757d",
                    color: "white",
                    fontSize: "16px",
                  }}
                >
                  <i className="fas fa-times me-2"></i>Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingCase}
                  style={{
                    padding: "12px 40px",
                    borderRadius: "8px",
                    border: "none",
                    cursor: submittingCase ? "not-allowed" : "pointer",
                    background: submittingCase ? "#adb5bd" : "var(--primary)",
                    color: "white",
                    fontSize: "16px",
                    fontWeight: "600",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  {submittingCase ? (
                    <>
                      <i className="fas fa-spinner fa-spin"></i>Submitting...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-save"></i>Submit Case
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // MAIN PORTAL
  const viewTitles = {
    dashboard: "Client Dashboard",
    "my-cases": "My Cases",
    "find-lawfirm": "Find Law Firm",
    messages: "Messages & Updates",
    "case-detail": "Case Details",
    profile: "Profile & Settings",
    "lawfirm-detail": "Law Firm Details",
  };
  const viewIcons = {
    dashboard: "tachometer-alt",
    "my-cases": "folder",
    "find-lawfirm": "search",
    messages: "comments",
    "case-detail": "file-alt",
    profile: "user-cog",
    "lawfirm-detail": "building",
  };

  return (
    <div className="client-portal-container">
      {apiError && (
        <div
          style={{
            backgroundColor: "#fff3cd",
            color: "#856404",
            padding: "10px 20px",
            textAlign: "center",
            borderBottom: "1px solid #ffeeba",
            position: "sticky",
            top: 0,
            zIndex: 1001,
            fontSize: "13px",
          }}
        >
          <i className="fas fa-exclamation-triangle me-2"></i>
          {apiError}
          <button
            onClick={() => setApiError(null)}
            style={{
              background: "none",
              border: "none",
              marginLeft: "15px",
              cursor: "pointer",
              color: "#856404",
            }}
          >
            <i className="fas fa-times"></i>
          </button>
        </div>
      )}

      <div className="container-fluid">
        {/* SIDEBAR */}
        <div className={`sidebar ${sidebarCollapsed ? "collapsed" : ""}`}>
          <div className="logo">
            <div className="logo-icon">
              <i className="fas fa-balance-scale"></i>
            </div>
            <div className="logo-text">Advocare</div>
          </div>
          <div className="sidebar-nav">
            {[
              { v: "dashboard", i: "tachometer-alt", l: "Dashboard" },
              {
                v: "my-cases",
                i: "folder",
                l: "My Cases",
                badge: cases.length,
              },
              {
                v: "find-lawfirm",
                i: "search",
                l: "Find Law Firm",
                action: () => {
                  setActiveView("find-lawfirm");
                  setShowAISection(false);
                  setShowLawFirmDetail(false);
                },
              },
              {
                v: "messages",
                i: "comments",
                l: "Messages & Updates",
                badge: unreadCount,
              },
              { v: "profile", i: "user-cog", l: "Profile & Settings" },
            ].map(({ v, i, l, badge, action }) => (
              <button
                key={v}
                className={`sidebar-item ${activeView === v ? "active" : ""}`}
                onClick={
                  action ||
                  (() => {
                    setActiveView(v);
                    setShowLawFirmDetail(false);
                  })
                }
              >
                <div className="sidebar-icon">
                  <i className={`fas fa-${i}`}></i>
                </div>
                <div className="nav-text">{l}</div>
                {badge > 0 && (
                  <span
                    style={{
                      background: "#dc3545",
                      color: "white",
                      borderRadius: "10px",
                      padding: "2px 7px",
                      fontSize: "11px",
                      marginLeft: "auto",
                    }}
                  >
                    {badge}
                  </span>
                )}
              </button>
            ))}
          </div>
          <div className="sidebar-actions">
            <div className="sidebar-actions-title">Quick Actions</div>
            <button
              className="sidebar-action-btn"
              onClick={() => setShowCreateCasePage(true)}
            >
              <i className="fas fa-plus-circle sidebar-actions-icon"></i>
              <span className="sidebar-actions-text">Create New Case</span>
            </button>
            <button
              className="sidebar-action-btn"
              onClick={() => {
                setActiveView("find-lawfirm");
                setShowAISection(false);
                setShowLawFirmDetail(false);
              }}
            >
              <i className="fas fa-search sidebar-actions-icon"></i>
              <span className="sidebar-actions-text">Find Law Firm</span>
            </button>
            <button
              className="sidebar-action-btn"
              onClick={() => {
                setActiveView("find-lawfirm");
                setShowAISection(true);
                setShowLawFirmDetail(false);
              }}
            >
              <i className="fas fa-robot sidebar-actions-icon"></i>
              <span className="sidebar-actions-text">AI Match</span>
            </button>
          </div>
          <div className="user-profile">
            <div className="user-avatar">
              {userData?.name?.charAt(0)?.toUpperCase() || "C"}
            </div>
            <div className="user-info">
              <h4>{userData?.name || "Client"}</h4>
              <p>Client Portal</p>
            </div>
          </div>
        </div>

        {/* MAIN CONTENT */}
        <div className="main-content">
          <div className="header">
            <div className="d-flex align-items-center">
              <div
                className="sidebar-toggle"
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              >
                <i className="fas fa-bars"></i>
              </div>
              <div className="page-title">
                <i className={`fas fa-${viewIcons[activeView]}`}></i>
                <span>{viewTitles[activeView]}</span>
              </div>
            </div>
            <div className="header-actions">
              <div className="search-bar">
                <i className="fas fa-search"></i>
                <input type="text" placeholder="Search cases..." />
              </div>
              <div className="notification-btn">
                <i className="fas fa-bell"></i>
                {unreadNotif > 0 && <div className="notification-dot"></div>}
              </div>
              <button className="btn-outline" onClick={handleLogout}>
                <i className="fas fa-sign-out-alt"></i> Logout
              </button>
            </div>
          </div>

          {/* DASHBOARD (unchanged) */}
          {activeView === "dashboard" && (
            <div>
              <div className="stats-cards">
                {[
                  {
                    n: stats.totalCases,
                    l: "Total Cases",
                    i: "folder-open",
                    c: "stat-card-1",
                  },
                  {
                    n: stats.activeCases,
                    l: "Active Cases",
                    i: "hourglass-half",
                    c: "stat-card-2",
                  },
                  {
                    n: stats.pendingRequests,
                    l: "Pending",
                    i: "clock",
                    c: "stat-card-3",
                  },
                  {
                    n: stats.completedCases,
                    l: "Completed",
                    i: "check-circle",
                    c: "stat-card-4",
                  },
                ].map(({ n, l, i, c }) => (
                  <div key={l} className={`stat-card ${c}`}>
                    <div className="stat-icon">
                      <i className={`fas fa-${i}`}></i>
                    </div>
                    <div>
                      <div className="stat-number">{n}</div>
                      <div className="stat-label">{l}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="dashboard-content">
                <div className="content-card">
                  <div className="card-title">
                    <i className="fas fa-chart-pie me-2"></i>Case Status
                    Overview
                  </div>
                  {cases.length === 0 ? (
                    <div
                      style={{
                        textAlign: "center",
                        padding: "40px",
                        color: "#6c757d",
                      }}
                    >
                      <i
                        className="fas fa-chart-pie"
                        style={{
                          fontSize: "48px",
                          color: "#c99c33",
                          marginBottom: "15px",
                          display: "block",
                        }}
                      ></i>
                      <p>
                        No cases yet. Create your first case to see analytics.
                      </p>
                      <button
                        className="btn-advocare"
                        onClick={() => setShowCreateCasePage(true)}
                      >
                        <i className="fas fa-plus-circle me-2"></i>Create First
                        Case
                      </button>
                    </div>
                  ) : (
                    <div className="chart-wrapper">
                      <canvas ref={chartRef}></canvas>
                    </div>
                  )}
                </div>
                <div className="content-card">
                  <div className="card-title">
                    <div>
                      <i className="fas fa-history me-2"></i>Recent Activity
                    </div>
                    <button
                      style={{
                        fontSize: "13px",
                        color: "var(--primary)",
                        background: "none",
                        border: "none",
                        cursor: "pointer",
                      }}
                      onClick={() => setActiveView("my-cases")}
                    >
                      View All
                    </button>
                  </div>
                  {cases.length === 0 ? (
                    <div
                      style={{
                        textAlign: "center",
                        padding: "30px",
                        color: "#6c757d",
                      }}
                    >
                      <i
                        className="fas fa-folder-open"
                        style={{
                          fontSize: "36px",
                          marginBottom: "10px",
                          display: "block",
                          color: "#c99c33",
                        }}
                      ></i>
                      <p>No cases yet.</p>
                    </div>
                  ) : (
                    <ul className="activity-list">
                      {cases.slice(0, 5).map((c) => (
                        <li key={c.id} className="activity-item">
                          <div
                            className="activity-icon"
                            style={{
                              backgroundColor: "var(--primary)",
                              color: "white",
                            }}
                          >
                            <i className="fas fa-gavel"></i>
                          </div>
                          <div className="activity-details">
                            <h4
                              style={{
                                cursor: "pointer",
                                color: "var(--primary)",
                              }}
                              onClick={() => viewCaseDetails(c)}
                            >
                              {c.title}
                            </h4>
                            <p>
                              <span
                                className={`case-status ${getStatusBadgeClass(c.status)}`}
                              >
                                {getStatusText(c.status)}
                              </span>
                            </p>
                            <div className="activity-date">
                              Updated:{" "}
                              {formatDate(c.updated_at || c.created_at)}
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
              <div className="quick-actions-grid">
                <button
                  className="action-btn-card"
                  onClick={() => setShowCreateCasePage(true)}
                >
                  <i className="fas fa-plus-circle"></i>
                  <span>Create New Case</span>
                </button>
                <button
                  className="action-btn-card"
                  onClick={() => {
                    setActiveView("find-lawfirm");
                    setShowAISection(false);
                  }}
                >
                  <i className="fas fa-search"></i>
                  <span>Find Law Firm</span>
                </button>
                <button
                  className="action-btn-card"
                  onClick={() => {
                    setActiveView("find-lawfirm");
                    setShowAISection(true);
                  }}
                >
                  <i className="fas fa-robot"></i>
                  <span>AI Match</span>
                </button>
                <button
                  className="action-btn-card"
                  onClick={() => setActiveView("messages")}
                >
                  <i className="fas fa-comments"></i>
                  <span>Messages</span>
                </button>
              </div>
              <div className="content-card">
                <div className="card-title">
                  <div>
                    <i className="fas fa-file-contract me-2"></i>My Cases (
                    {cases.length})
                  </div>
                  <button
                    className="btn-advocare btn-sm"
                    onClick={() => setShowCreateCasePage(true)}
                  >
                    <i className="fas fa-plus me-1"></i>New Case
                  </button>
                </div>
                <div className="table-responsive">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Case</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Law Firm</th>
                        <th>Date</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cases.length === 0 ? (
                        <tr>
                          <td
                            colSpan="6"
                            style={{
                              textAlign: "center",
                              padding: "30px",
                              color: "#6c757d",
                            }}
                          >
                            No cases found.{" "}
                            <button
                              onClick={() => setShowCreateCasePage(true)}
                              style={{
                                color: "var(--primary)",
                                background: "none",
                                border: "none",
                                cursor: "pointer",
                                textDecoration: "underline",
                              }}
                            >
                              Create your first case
                            </button>
                          </td>
                        </tr>
                      ) : (
                        cases.slice(0, 5).map((c) => (
                          <tr key={c.id}>
                            <td>
                              <strong>{c.title}</strong>
                              <br />
                              <small className="text-muted">#{c.id}</small>
                            </td>
                            <td>
                              <span className="case-type">
                                {c.case_type || "—"}
                              </span>
                            </td>
                            <td>
                              <span
                                className={`case-status ${getStatusBadgeClass(c.status)}`}
                              >
                                {getStatusText(c.status)}
                              </span>
                            </td>
                            <td>{c.law_firm_name || c.law_firm || "—"}</td>
                            <td>{formatDate(c.created_at)}</td>
                            <td>
                              <button
                                className="btn-advocare btn-sm"
                                onClick={() => viewCaseDetails(c)}
                              >
                                View
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* MY CASES (unchanged) */}
          {activeView === "my-cases" && (
            <div className="content-card">
              <div className="card-title">
                <span>
                  <i className="fas fa-folder me-2"></i>My Cases ({cases.length}
                  )
                </span>
                <button
                  className="btn-advocare"
                  onClick={() => setShowCreateCasePage(true)}
                >
                  <i className="fas fa-plus-circle me-2"></i>Create New Case
                </button>
              </div>
              {cases.length === 0 ? (
                <div
                  style={{
                    textAlign: "center",
                    padding: "60px 20px",
                    color: "#6c757d",
                  }}
                >
                  <i
                    className="fas fa-folder-open"
                    style={{
                      fontSize: "60px",
                      color: "#c99c33",
                      marginBottom: "20px",
                      display: "block",
                    }}
                  ></i>
                  <h5 style={{ color: "#1a365d", marginBottom: "10px" }}>
                    No Cases Found
                  </h5>
                  <p>You haven't created any cases yet.</p>
                  <div
                    style={{
                      display: "flex",
                      gap: "15px",
                      justifyContent: "center",
                    }}
                  >
                    <button
                      className="btn-advocare"
                      onClick={() => setShowCreateCasePage(true)}
                    >
                      <i className="fas fa-plus-circle me-2"></i>Create New Case
                    </button>
                    <button
                      style={{
                        padding: "10px 20px",
                        background: "#6c757d",
                        color: "white",
                        border: "none",
                        borderRadius: "6px",
                        cursor: "pointer",
                      }}
                      onClick={loadCases}
                    >
                      <i className="fas fa-sync me-2"></i>Refresh Cases
                    </button>
                  </div>
                </div>
              ) : (
                <div className="row">
                  {cases.map((c) => (
                    <div key={c.id} className="col-lg-4 col-md-6 mb-4">
                      <div
                        className="case-card"
                        style={{ borderLeft: "4px solid var(--primary)" }}
                      >
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "flex-start",
                            marginBottom: "10px",
                          }}
                        >
                          <h6
                            style={{
                              margin: 0,
                              fontWeight: "600",
                              color: "var(--primary)",
                              flex: 1,
                            }}
                          >
                            {c.title}
                          </h6>
                          <span
                            className={`case-status ${getStatusBadgeClass(c.status)}`}
                          >
                            {getStatusText(c.status)}
                          </span>
                        </div>
                        <div className="mb-2">
                          <span className="case-type">
                            {c.case_type || "General"}
                          </span>
                        </div>
                        <div className="mb-2">
                          <small className="text-muted">Law Firm:</small>
                          <div style={{ fontWeight: "500", fontSize: "14px" }}>
                            {c.law_firm_name || c.law_firm || "Not assigned"}
                          </div>
                        </div>
                        <div className="mb-3">
                          <small className="text-muted">
                            Created: {formatDate(c.created_at)}
                          </small>
                        </div>
                        <div
                          style={{
                            display: "flex",
                            gap: "8px",
                            flexWrap: "wrap",
                          }}
                        >
                          <button
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => viewCaseDetails(c)}
                          >
                            <i className="fas fa-eye me-1"></i>View
                          </button>
                          <button
                            className="btn btn-sm btn-outline-secondary"
                            onClick={() => {
                              setSelectedDocCase(c);
                              setShowDocModal(true);
                            }}
                          >
                            <i className="fas fa-upload me-1"></i>Upload
                          </button>
                          {(c.law_firm_id || c.law_firm) && (
                            <button
                              className="btn btn-sm btn-outline-info"
                              onClick={() =>
                                openChat(c, {
                                  firm_name: c.law_firm_name,
                                  id: c.law_firm_id || c.law_firm,
                                })
                              }
                            >
                              <i className="fas fa-comment me-1"></i>Message
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* FIND LAW FIRM & AI MATCH (updated with Details button navigation) */}
          {activeView === "find-lawfirm" && (
            <div>
              <div
                style={{
                  display: "flex",
                  marginBottom: "25px",
                  background: "white",
                  borderRadius: "10px",
                  padding: "5px",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                }}
              >
                <button
                  onClick={() => {
                    setShowAISection(false);
                    setShowLawFirmDetail(false);
                  }}
                  style={{
                    flex: 1,
                    padding: "12px 20px",
                    border: "none",
                    borderRadius: "8px",
                    fontWeight: "600",
                    cursor: "pointer",
                    background: !showAISection
                      ? "var(--primary)"
                      : "transparent",
                    color: !showAISection ? "white" : "#6c757d",
                  }}
                >
                  <i className="fas fa-search me-2"></i>Browse Law Firms
                </button>
                <button
                  onClick={() => {
                    setShowAISection(true);
                    setShowLawFirmDetail(false);
                  }}
                  style={{
                    flex: 1,
                    padding: "12px 20px",
                    border: "none",
                    borderRadius: "8px",
                    fontWeight: "600",
                    cursor: "pointer",
                    background: showAISection
                      ? "var(--primary)"
                      : "transparent",
                    color: showAISection ? "white" : "#6c757d",
                  }}
                >
                  <i className="fas fa-robot me-2"></i>AI Match
                </button>
              </div>

              {!showAISection && (
                <div className="content-card">
                  <div className="card-title">
                    <span>
                      <i className="fas fa-building me-2"></i>
                      {lawFirmsLoading
                        ? "Loading Law Firms..."
                        : `Approved Law Firms (${filterLawFirms().length})`}
                    </span>
                    <div style={{ display: "flex", gap: "10px" }}>
                      <button
                        className="btn-advocare btn-sm"
                        onClick={() => setShowFilterModal(true)}
                      >
                        <i className="fas fa-sliders-h me-1"></i>Filters
                      </button>
                      <button
                        style={{
                          padding: "6px 14px",
                          background: "#6c757d",
                          color: "white",
                          border: "none",
                          borderRadius: "6px",
                          cursor: "pointer",
                          fontSize: "13px",
                        }}
                        onClick={loadLawFirms}
                      >
                        <i className="fas fa-sync me-1"></i>Refresh
                      </button>
                    </div>
                  </div>
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(3,1fr)",
                      gap: "15px",
                      marginBottom: "20px",
                    }}
                  >
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Specialization..."
                      value={searchFilters.specialization}
                      onChange={(e) =>
                        setSearchFilters({
                          ...searchFilters,
                          specialization: e.target.value,
                        })
                      }
                    />
                    <input
                      type="text"
                      className="form-control"
                      placeholder="City / Location..."
                      value={searchFilters.location}
                      onChange={(e) =>
                        setSearchFilters({
                          ...searchFilters,
                          location: e.target.value,
                        })
                      }
                    />
                    <input
                      type="number"
                      className="form-control"
                      placeholder="Min Experience (Years)"
                      value={searchFilters.experience}
                      onChange={(e) =>
                        setSearchFilters({
                          ...searchFilters,
                          experience: e.target.value,
                        })
                      }
                    />
                  </div>
                  {lawFirmsLoading ? (
                    <div style={{ textAlign: "center", padding: "50px" }}>
                      <div className="spinner"></div>
                      <p>Loading law firms...</p>
                    </div>
                  ) : lawFirms.length === 0 ? (
                    <div
                      style={{
                        textAlign: "center",
                        padding: "50px",
                        color: "#6c757d",
                      }}
                    >
                      <i
                        className="fas fa-building"
                        style={{
                          fontSize: "48px",
                          color: "#c99c33",
                          marginBottom: "15px",
                          display: "block",
                        }}
                      ></i>
                      <h5>No Approved Law Firms Yet</h5>
                      <p>Law firms appear here once approved by admin.</p>
                      <button
                        style={{
                          marginTop: "15px",
                          padding: "10px 25px",
                          background: "var(--primary)",
                          color: "white",
                          border: "none",
                          borderRadius: "6px",
                          cursor: "pointer",
                        }}
                        onClick={loadLawFirms}
                      >
                        <i className="fas fa-sync me-2"></i>Try Again
                      </button>
                    </div>
                  ) : filterLawFirms().length === 0 ? (
                    <div
                      style={{
                        textAlign: "center",
                        padding: "40px",
                        color: "#6c757d",
                      }}
                    >
                      <p>
                        No firms match your filters.{" "}
                        <button
                          onClick={() =>
                            setSearchFilters({
                              specialization: "",
                              location: "",
                              experience: "",
                              rating: "",
                              language: "",
                            })
                          }
                          style={{
                            color: "var(--primary)",
                            background: "none",
                            border: "none",
                            cursor: "pointer",
                            textDecoration: "underline",
                          }}
                        >
                          Clear filters
                        </button>
                      </p>
                    </div>
                  ) : (
                    <div className="row">
                      {filterLawFirms().map((firm) => (
                        <div key={firm.id} className="col-lg-4 col-md-6 mb-4">
                          <div
                            style={{
                              background: "white",
                              borderRadius: "12px",
                              padding: "20px",
                              borderTop: "3px solid var(--primary)",
                              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                              height: "100%",
                              display: "flex",
                              flexDirection: "column",
                            }}
                          >
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                marginBottom: "12px",
                              }}
                            >
                              <div
                                style={{
                                  width: "45px",
                                  height: "45px",
                                  borderRadius: "10px",
                                  background: "var(--primary)",
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                  marginRight: "12px",
                                }}
                              >
                                <i
                                  className="fas fa-balance-scale"
                                  style={{ color: "white", fontSize: "18px" }}
                                ></i>
                              </div>
                              <div>
                                <h6
                                  style={{
                                    margin: 0,
                                    fontWeight: "700",
                                    color: "var(--primary)",
                                  }}
                                >
                                  {getFirmName(firm)}
                                </h6>
                                <span
                                  style={{
                                    fontSize: "11px",
                                    background: "#e8f4fd",
                                    color: "#1565c0",
                                    padding: "2px 8px",
                                    borderRadius: "10px",
                                  }}
                                >
                                  ✓ Verified
                                </span>
                              </div>
                            </div>
                            <p
                              style={{
                                fontSize: "13px",
                                color: "#6c757d",
                                marginBottom: "6px",
                              }}
                            >
                              <i className="fas fa-gavel me-1"></i>
                              {getFirmSpec(firm)}
                            </p>
                            <p
                              style={{
                                fontSize: "13px",
                                color: "#6c757d",
                                marginBottom: "12px",
                              }}
                            >
                              <i className="fas fa-map-marker-alt me-1"></i>
                              {getFirmLocation(firm)}
                            </p>
                            <div
                              style={{
                                background: "#f8f9fa",
                                borderRadius: "8px",
                                padding: "10px",
                                marginBottom: "12px",
                                fontSize: "13px",
                              }}
                            >
                              <div
                                style={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  marginBottom: "4px",
                                }}
                              >
                                <span>Experience:</span>
                                <strong>
                                  {firm.experience ||
                                    firm.years_of_experience ||
                                    "5"}
                                  + yrs
                                </strong>
                              </div>
                              <div
                                style={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  marginBottom: "4px",
                                }}
                              >
                                <span>Success Rate:</span>
                                <strong style={{ color: "#28a745" }}>
                                  {firm.success_rate || "85"}%
                                </strong>
                              </div>
                              <div
                                style={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                }}
                              >
                                <span>Rating:</span>
                                <strong>
                                  <i
                                    className="fas fa-star"
                                    style={{ color: "#ffc107" }}
                                  ></i>{" "}
                                  {firm.rating || firm.average_rating || "4.5"}
                                </strong>
                              </div>
                            </div>
                            <div
                              style={{
                                display: "flex",
                                gap: "8px",
                                marginTop: "auto",
                              }}
                            >
                              <button
                                className="btn btn-sm btn-outline-primary"
                                style={{ flex: 1 }}
                                onClick={() => viewLawFirmDetails(firm)}
                              >
                                Details
                              </button>
                              <button
                                className="btn-advocare btn-sm"
                                style={{ flex: 1 }}
                                onClick={() => openAssignModal(firm)}
                              >
                                Assign Case
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Assign Modal */}
              {showAssignModal && selectedFirmForAssign && (
                <div
                  className="modal-overlay"
                  onClick={() => setShowAssignModal(false)}
                >
                  <div
                    className="modal-container"
                    style={{ maxWidth: "500px" }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <div className="modal-header">
                      <h5>
                        Assign Case to {getFirmName(selectedFirmForAssign)}
                      </h5>
                      <button
                        className="modal-close"
                        onClick={() => setShowAssignModal(false)}
                      >
                        &times;
                      </button>
                    </div>
                    <div className="p-3">
                      <label className="fw-bold mb-2">
                        Select which case to assign:
                      </label>
                      <select
                        className="form-control mb-3"
                        value={selectedCaseToAssign}
                        onChange={(e) =>
                          setSelectedCaseToAssign(e.target.value)
                        }
                      >
                        {cases
                          .filter((c) => c.status === "pending")
                          .map((c) => (
                            <option key={c.id} value={c.id}>
                              {c.title} (ID: #{c.id}) - Created:{" "}
                              {formatDate(c.created_at)}
                            </option>
                          ))}
                      </select>
                      <div className="alert alert-info mb-3">
                        <i className="fas fa-info-circle me-2"></i>This will
                        send a request to the law firm. They will review and
                        accept your case.
                      </div>
                      <div className="d-flex justify-content-end gap-2">
                        <button
                          className="btn-secondary"
                          onClick={() => setShowAssignModal(false)}
                        >
                          Cancel
                        </button>
                        <button
                          className="btn-primary"
                          onClick={assignCaseToFirm}
                          disabled={assigningCase}
                        >
                          {assigningCase
                            ? "Assigning..."
                            : "Send Request to Law Firm"}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* AI Match */}
              {showAISection && (
                <div className="content-card">
                  <div className="card-title">
                    <i
                      className="fas fa-robot me-2"
                      style={{ color: "#c99c33" }}
                    ></i>
                    AI-Powered Law Firm Matching
                  </div>
                  <div
                    style={{
                      background: "linear-gradient(135deg, #f8f9fa, #e8f4fd)",
                      borderRadius: "10px",
                      padding: "20px",
                      marginBottom: "20px",
                    }}
                  >
                    <p>
                      <i
                        className="fas fa-info-circle me-2"
                        style={{ color: "#c99c33" }}
                      ></i>
                      AI analyzes your case description and recommends the best{" "}
                      <strong>verified & approved</strong> law firms based on
                      specialization matching.
                    </p>
                    <textarea
                      className="form-control"
                      rows="4"
                      placeholder="Describe your case in detail (e.g., On 10 March 2026, I was physically assaulted by my neighbor...)"
                      value={aiCaseDesc}
                      onChange={(e) => setAiCaseDesc(e.target.value)}
                      style={{ marginBottom: "12px" }}
                    />
                    <button
                      className="btn-advocare"
                      style={{ width: "100%", padding: "12px" }}
                      onClick={getAIRecommendations}
                      disabled={aiLoading || !aiCaseDesc.trim()}
                    >
                      {aiLoading ? (
                        <>
                          <i className="fas fa-spinner fa-spin me-2"></i>
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-magic me-2"></i>Get AI
                          Recommendations
                        </>
                      )}
                    </button>
                  </div>
                  {aiRecommendations.length > 0 && (
                    <div>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "15px",
                          marginBottom: "20px",
                        }}
                      >
                        <h5>Recommended Law Firms</h5>
                        <span
                          style={{
                            background: "#d4edda",
                            color: "#155724",
                            padding: "4px 12px",
                            borderRadius: "20px",
                            fontSize: "12px",
                          }}
                        >
                          <i className="fas fa-brain me-1"></i>AI Accuracy: ~92%
                        </span>
                      </div>
                      <div className="row">
                        {aiRecommendations.map((firm, idx) => {
                          const bc =
                            idx === 0
                              ? "#28a745"
                              : idx === 1
                                ? "#ffc107"
                                : "#17a2b8";
                          return (
                            <div
                              key={firm.id || idx}
                              className="col-lg-4 col-md-6 mb-4"
                            >
                              <div
                                style={{
                                  background: "white",
                                  borderRadius: "12px",
                                  padding: "20px",
                                  border: `2px solid ${bc}`,
                                  position: "relative",
                                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                                }}
                              >
                                <div
                                  style={{
                                    position: "absolute",
                                    top: 0,
                                    right: 0,
                                    background: bc,
                                    color: "white",
                                    padding: "4px 12px",
                                    borderBottomLeftRadius: "10px",
                                    fontSize: "12px",
                                    fontWeight: "700",
                                  }}
                                >
                                  #{idx + 1} Match
                                </div>
                                <div
                                  style={{
                                    display: "flex",
                                    alignItems: "center",
                                    marginBottom: "12px",
                                  }}
                                >
                                  <div
                                    style={{
                                      width: "45px",
                                      height: "45px",
                                      borderRadius: "10px",
                                      background: "var(--primary)",
                                      display: "flex",
                                      alignItems: "center",
                                      justifyContent: "center",
                                      marginRight: "12px",
                                    }}
                                  >
                                    <i
                                      className="fas fa-balance-scale"
                                      style={{ color: "white" }}
                                    ></i>
                                  </div>
                                  <div>
                                    <h6
                                      style={{ margin: 0, fontWeight: "700" }}
                                    >
                                      {getFirmName(firm)}
                                    </h6>
                                    <span
                                      style={{
                                        fontSize: "11px",
                                        background: "#e8f4fd",
                                        color: "#1565c0",
                                        padding: "2px 8px",
                                        borderRadius: "10px",
                                      }}
                                    >
                                      ✓ Verified
                                    </span>
                                  </div>
                                </div>
                                <div
                                  style={{
                                    display: "grid",
                                    gridTemplateColumns: "1fr 1fr",
                                    gap: "8px",
                                    marginBottom: "12px",
                                  }}
                                >
                                  <div
                                    style={{
                                      background: "#f0fff4",
                                      borderRadius: "8px",
                                      padding: "10px",
                                      textAlign: "center",
                                    }}
                                  >
                                    <div
                                      style={{
                                        fontWeight: "800",
                                        fontSize: "22px",
                                        color: "#28a745",
                                      }}
                                    >
                                      {firm.match_percentage || 90 - idx * 8}%
                                    </div>
                                    <div
                                      style={{
                                        fontSize: "11px",
                                        color: "#6c757d",
                                      }}
                                    >
                                      Case Match
                                    </div>
                                  </div>
                                  <div
                                    style={{
                                      background: "#fff8e1",
                                      borderRadius: "8px",
                                      padding: "10px",
                                      textAlign: "center",
                                    }}
                                  >
                                    <div
                                      style={{
                                        fontWeight: "800",
                                        fontSize: "22px",
                                        color: "#ff9800",
                                      }}
                                    >
                                      {firm.ai_accuracy || 92}%
                                    </div>
                                    <div
                                      style={{
                                        fontSize: "11px",
                                        color: "#6c757d",
                                      }}
                                    >
                                      AI Score
                                    </div>
                                  </div>
                                </div>
                                <div
                                  style={{
                                    background: "#f8f9fa",
                                    borderRadius: "8px",
                                    padding: "10px",
                                    marginBottom: "12px",
                                    fontSize: "12px",
                                  }}
                                >
                                  <div
                                    style={{
                                      display: "flex",
                                      justifyContent: "space-between",
                                    }}
                                  >
                                    <span>Specialization:</span>
                                    <strong>{getFirmSpec(firm)}</strong>
                                  </div>
                                  <div
                                    style={{
                                      display: "flex",
                                      justifyContent: "space-between",
                                      marginTop: "4px",
                                    }}
                                  >
                                    <span>Experience:</span>
                                    <strong>
                                      {firm.experience || "5"}+ yrs
                                    </strong>
                                  </div>
                                  <div
                                    style={{
                                      display: "flex",
                                      justifyContent: "space-between",
                                      marginTop: "4px",
                                    }}
                                  >
                                    <span>Success Rate:</span>
                                    <strong style={{ color: "#28a745" }}>
                                      {firm.success_rate || "85%"}
                                    </strong>
                                  </div>
                                </div>
                                <button
                                  className="btn-advocare"
                                  style={{ width: "100%", padding: "10px" }}
                                  onClick={() => openAssignModal(firm)}
                                >
                                  <i className="fas fa-paper-plane me-2"></i>
                                  Assign My Case
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* LAW FIRM DETAIL PAGE - New View */}
          {activeView === "lawfirm-detail" && selectedLawFirm && (
            <div className="row">
              <div className="col-lg-8">
                <div className="content-card mb-4">
                  <div className="card-title">
                    <span>
                      <i className="fas fa-building me-2"></i>Law Firm Profile
                    </span>
                    <button
                      className="btn-outline btn-sm"
                      onClick={() => {
                        setActiveView("find-lawfirm");
                        setShowLawFirmDetail(false);
                      }}
                    >
                      <i className="fas fa-arrow-left me-2"></i>Back to List
                    </button>
                  </div>
                  <div className="row mb-4">
                    <div className="col-md-8">
                      <h3 style={{ color: "var(--primary)" }}>
                        {getFirmName(selectedLawFirm)}
                      </h3>
                      <p>
                        <span
                          style={{
                            background: "#e8f4fd",
                            color: "#1565c0",
                            padding: "4px 12px",
                            borderRadius: "20px",
                            fontSize: "13px",
                          }}
                        >
                          ✓ Verified & Approved
                        </span>
                      </p>
                    </div>
                    <div className="col-md-4 text-md-end">
                      <div className="rating-display">
                        <i
                          className="fas fa-star"
                          style={{ color: "#ffc107" }}
                        ></i>{" "}
                        {selectedLawFirm.rating ||
                          selectedLawFirm.average_rating ||
                          "4.5"}{" "}
                        / 5
                      </div>
                    </div>
                  </div>
                  <div className="row mb-4">
                    <div className="col-md-6">
                      <h6>
                        <i className="fas fa-gavel me-2"></i>Specialization
                      </h6>
                      <p>{getFirmSpec(selectedLawFirm)}</p>
                      <h6>
                        <i className="fas fa-map-marker-alt me-2"></i>Location
                      </h6>
                      <p>{getFirmLocation(selectedLawFirm)}</p>
                      <h6>
                        <i className="fas fa-calendar-alt me-2"></i>Experience
                      </h6>
                      <p>
                        {selectedLawFirm.experience ||
                          selectedLawFirm.years_of_experience ||
                          "5"}
                        + years
                      </p>
                    </div>
                    <div className="col-md-6">
                      <h6>
                        <i className="fas fa-phone me-2"></i>Contact
                      </h6>
                      <p>{selectedLawFirm.phone || "Not provided"}</p>
                      <h6>
                        <i className="fas fa-envelope me-2"></i>Email
                      </h6>
                      <p>{selectedLawFirm.email || "Not provided"}</p>
                      <h6>
                        <i className="fas fa-chart-line me-2"></i>Success Rate
                      </h6>
                      <p>
                        <strong style={{ color: "#28a745" }}>
                          {selectedLawFirm.success_rate || "85"}%
                        </strong>{" "}
                        of cases won
                      </p>
                    </div>
                  </div>
                  <div className="alert alert-info">
                    <i className="fas fa-info-circle me-2"></i> This law firm
                    has been verified by our team. You can assign your pending
                    case to them for legal representation.
                  </div>
                  <div className="d-flex gap-3 mt-3">
                    <button
                      className="btn-advocare"
                      onClick={() => openAssignModal(selectedLawFirm)}
                    >
                      <i className="fas fa-paper-plane me-2"></i>Assign My Case
                    </button>
                    <button
                      className="btn-outline"
                      onClick={() => {
                        setActiveView("find-lawfirm");
                        setShowLawFirmDetail(false);
                      }}
                    >
                      Browse More Firms
                    </button>
                  </div>
                </div>
              </div>
              <div className="col-lg-4">
                <div className="content-card">
                  <h6 className="card-title">
                    <i className="fas fa-star me-2"></i>Client Reviews
                  </h6>
                  <p style={{ color: "#6c757d" }}>
                    No reviews yet. Be the first to share your experience after
                    case resolution.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* MESSAGES (unchanged) */}
          {activeView === "messages" && (
            <div>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "300px 1fr",
                  gap: "20px",
                  minHeight: "550px",
                }}
              >
                <div
                  style={{
                    background: "white",
                    borderRadius: "12px",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                    overflow: "hidden",
                    display: "flex",
                    flexDirection: "column",
                  }}
                >
                  <div
                    style={{
                      padding: "18px 20px",
                      background: "var(--primary)",
                      color: "white",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <h6 style={{ margin: 0, fontWeight: "700" }}>
                      <i className="fas fa-comments me-2"></i>Conversations
                    </h6>
                    <div>
                      <div
                        style={{
                          width: "8px",
                          height: "8px",
                          borderRadius: "50%",
                          background: "#28a745",
                          boxShadow: "0 0 6px #28a745",
                        }}
                      ></div>
                      <small>Live</small>
                    </div>
                  </div>
                  <div style={{ flex: 1, overflowY: "auto" }}>
                    {cases.filter((c) => c.law_firm_id || c.law_firm).length ===
                    0 ? (
                      <div
                        style={{
                          padding: "40px 20px",
                          textAlign: "center",
                          color: "#6c757d",
                        }}
                      >
                        <i
                          className="fas fa-comment-slash"
                          style={{
                            fontSize: "40px",
                            marginBottom: "12px",
                            display: "block",
                            color: "#c99c33",
                          }}
                        ></i>
                        <p>No active conversations</p>
                        <p style={{ fontSize: "12px" }}>
                          Assign a case to a law firm to start messaging
                        </p>
                      </div>
                    ) : (
                      cases
                        .filter((c) => c.law_firm_id || c.law_firm)
                        .map((c) => (
                          <div
                            key={c.id}
                            onClick={() =>
                              openChat(c, {
                                firm_name: c.law_firm_name,
                                id: c.law_firm_id || c.law_firm,
                              })
                            }
                            style={{
                              padding: "15px 20px",
                              borderBottom: "1px solid #e9ecef",
                              cursor: "pointer",
                              background:
                                selectedChat?.caseId === c.id
                                  ? "#e3f2fd"
                                  : "transparent",
                              borderLeft:
                                selectedChat?.caseId === c.id
                                  ? "3px solid var(--primary)"
                                  : "3px solid transparent",
                            }}
                          >
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "10px",
                              }}
                            >
                              <div
                                style={{
                                  width: "40px",
                                  height: "40px",
                                  borderRadius: "50%",
                                  background: "var(--primary)",
                                  color: "white",
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                  fontWeight: "700",
                                }}
                              >
                                {(c.law_firm_name || "L")
                                  .charAt(0)
                                  .toUpperCase()}
                              </div>
                              <div style={{ flex: 1 }}>
                                <div
                                  style={{
                                    fontWeight: "600",
                                    fontSize: "14px",
                                    color: "var(--primary)",
                                  }}
                                >
                                  {c.law_firm_name || "Law Firm"}
                                </div>
                                <div
                                  style={{ fontSize: "12px", color: "#6c757d" }}
                                >
                                  {c.title}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))
                    )}
                  </div>
                </div>
                <div
                  style={{
                    background: "white",
                    borderRadius: "12px",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                    display: "flex",
                    flexDirection: "column",
                    overflow: "hidden",
                  }}
                >
                  {!selectedChat ? (
                    <div
                      style={{
                        flex: 1,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: "40px",
                        color: "#6c757d",
                      }}
                    >
                      <i
                        className="fas fa-comments"
                        style={{
                          fontSize: "64px",
                          color: "#c99c33",
                          marginBottom: "20px",
                        }}
                      ></i>
                      <h5>Select a Conversation</h5>
                      <p>Choose a case from the left to start messaging.</p>
                    </div>
                  ) : (
                    <>
                      <div
                        style={{
                          padding: "15px 20px",
                          borderBottom: "1px solid #e9ecef",
                          background: "#f8f9fa",
                          display: "flex",
                          alignItems: "center",
                          gap: "12px",
                        }}
                      >
                        <div
                          style={{
                            width: "42px",
                            height: "42px",
                            borderRadius: "50%",
                            background: "var(--primary)",
                            color: "white",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontWeight: "700",
                          }}
                        >
                          {(selectedChat.firmName || "L")
                            .charAt(0)
                            .toUpperCase()}
                        </div>
                        <div>
                          <div
                            style={{
                              fontWeight: "700",
                              color: "var(--primary)",
                            }}
                          >
                            {selectedChat.firmName}
                          </div>
                          <div style={{ fontSize: "12px", color: "#6c757d" }}>
                            Case:{" "}
                            {
                              cases.find((c) => c.id === selectedChat.caseId)
                                ?.title
                            }
                            <span
                              style={{ marginLeft: "10px", color: "#28a745" }}
                            >
                              ● Live
                            </span>
                          </div>
                        </div>
                      </div>
                      <div
                        style={{
                          flex: 1,
                          overflowY: "auto",
                          padding: "20px",
                          display: "flex",
                          flexDirection: "column",
                          gap: "12px",
                          minHeight: "350px",
                          maxHeight: "420px",
                        }}
                      >
                        {chatMessages.length === 0 ? (
                          <div
                            style={{
                              textAlign: "center",
                              color: "#6c757d",
                              marginTop: "40px",
                            }}
                          >
                            <i
                              className="fas fa-comment-dots"
                              style={{
                                fontSize: "36px",
                                marginBottom: "10px",
                                display: "block",
                              }}
                            ></i>
                            <p>No messages yet. Start the conversation!</p>
                          </div>
                        ) : (
                          chatMessages.map((msg) => (
                            <div
                              key={msg.id}
                              style={{
                                display: "flex",
                                justifyContent:
                                  msg.sender_role === "client"
                                    ? "flex-end"
                                    : "flex-start",
                              }}
                            >
                              <div
                                style={{
                                  maxWidth: "70%",
                                  padding: "10px 15px",
                                  borderRadius:
                                    msg.sender_role === "client"
                                      ? "18px 18px 4px 18px"
                                      : "18px 18px 18px 4px",
                                  background:
                                    msg.sender_role === "client"
                                      ? "var(--primary)"
                                      : "#f1f1f1",
                                  color:
                                    msg.sender_role === "client"
                                      ? "white"
                                      : "#333",
                                }}
                              >
                                <p
                                  style={{
                                    margin: "0 0 4px 0",
                                    fontSize: "14px",
                                  }}
                                >
                                  {msg.content}
                                </p>
                                <small
                                  style={{ fontSize: "10px", opacity: 0.75 }}
                                >
                                  {formatDate(msg.created_at)}
                                </small>
                              </div>
                            </div>
                          ))
                        )}
                        <div ref={chatEndRef} />
                      </div>
                      <div
                        style={{
                          padding: "15px 20px",
                          borderTop: "1px solid #e9ecef",
                          display: "flex",
                          gap: "10px",
                        }}
                      >
                        <input
                          type="text"
                          className="form-control"
                          placeholder="Type your message..."
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
                        />
                        <button className="btn-advocare" onClick={sendMessage}>
                          <i className="fas fa-paper-plane me-1"></i>Send
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>
              <div className="content-card" style={{ marginTop: "20px" }}>
                <div className="card-title">
                  <div>
                    <i
                      className="fas fa-bell me-2"
                      style={{ color: "#c99c33" }}
                    ></i>
                    System Notifications
                  </div>
                  {unreadNotif > 0 && (
                    <span
                      style={{
                        background: "#dc3545",
                        color: "white",
                        padding: "3px 10px",
                        borderRadius: "20px",
                        fontSize: "12px",
                      }}
                    >
                      {unreadNotif} unread
                    </span>
                  )}
                </div>
                {notifications.length === 0 ? (
                  <div
                    style={{
                      textAlign: "center",
                      padding: "30px",
                      color: "#6c757d",
                    }}
                  >
                    <i
                      className="fas fa-bell-slash"
                      style={{
                        fontSize: "36px",
                        marginBottom: "10px",
                        display: "block",
                        color: "#c99c33",
                      }}
                    ></i>
                    <p>No notifications yet.</p>
                  </div>
                ) : (
                  notifications.slice(0, 10).map((n) => (
                    <div
                      key={n.id}
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: "12px",
                        padding: "12px 0",
                        borderBottom: "1px solid #e9ecef",
                      }}
                    >
                      <div
                        style={{
                          width: "36px",
                          height: "36px",
                          borderRadius: "8px",
                          background: n.is_read ? "#f8f9fa" : "var(--primary)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        <i
                          className="fas fa-bell"
                          style={{
                            color: n.is_read ? "#6c757d" : "white",
                            fontSize: "14px",
                          }}
                        ></i>
                      </div>
                      <div>
                        <p
                          style={{
                            margin: 0,
                            fontWeight: n.is_read ? "400" : "600",
                            color: n.is_read ? "#6c757d" : "#333",
                            fontSize: "14px",
                          }}
                        >
                          {n.message}
                        </p>
                        <small style={{ color: "#6c757d" }}>
                          {formatDate(n.created_at)}
                        </small>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* PROFILE & SETTINGS - with Edit Button */}
          {activeView === "profile" && (
            <div className="row">
              <div className="col-lg-4">
                <div className="content-card text-center">
                  <div
                    style={{
                      width: "100px",
                      height: "100px",
                      borderRadius: "50%",
                      background: "var(--primary)",
                      color: "white",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "42px",
                      fontWeight: "700",
                      margin: "0 auto 15px",
                    }}
                  >
                    {userData?.name?.charAt(0)?.toUpperCase() || "C"}
                  </div>
                  <h5 style={{ color: "var(--primary)" }}>{userData?.name}</h5>
                  <p className="text-muted">{userData?.email}</p>
                  <span
                    style={{
                      background: "#d4edda",
                      color: "#155724",
                      padding: "4px 15px",
                      borderRadius: "20px",
                      fontSize: "13px",
                      fontWeight: "600",
                    }}
                  >
                    ✓ Approved Client
                  </span>
                  <div
                    style={{
                      marginTop: "20px",
                      padding: "15px",
                      background: "#f8f9fa",
                      borderRadius: "8px",
                      textAlign: "left",
                    }}
                  >
                    <div style={{ fontSize: "14px", marginBottom: "8px" }}>
                      <strong>Total Cases:</strong> {stats.totalCases}
                    </div>
                    <div style={{ fontSize: "14px", marginBottom: "8px" }}>
                      <strong>Active Cases:</strong> {stats.activeCases}
                    </div>
                    <div style={{ fontSize: "14px" }}>
                      <strong>Completed:</strong> {stats.completedCases}
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-lg-8">
                <div className="content-card">
                  <div className="card-title">
                    <span>
                      <i className="fas fa-user me-2"></i>Personal Details
                    </span>
                    {!profileEditMode ? (
                      <button
                        className="btn-advocare btn-sm"
                        onClick={() => setProfileEditMode(true)}
                      >
                        <i className="fas fa-edit me-1"></i>Edit Profile
                      </button>
                    ) : (
                      <div className="d-flex gap-2">
                        <button
                          className="btn-outline btn-sm"
                          onClick={() => {
                            setProfileEditMode(false);
                            setEditedProfile({
                              name: userData?.name || "",
                              email: userData?.email || "",
                              phone: userData?.phone || "",
                              city: userData?.city || "",
                            });
                          }}
                        >
                          Cancel
                        </button>
                        <button
                          className="btn-advocare btn-sm"
                          onClick={() => updateClientProfile(editedProfile)}
                        >
                          Save Changes
                        </button>
                      </div>
                    )}
                  </div>
                  <div className="row mb-3">
                    <div className="col-md-6">
                      <label className="form-label fw-bold">Full Name</label>
                      <input
                        type="text"
                        className="form-control"
                        value={
                          profileEditMode
                            ? editedProfile.name
                            : userData?.name || ""
                        }
                        readOnly={!profileEditMode}
                        onChange={(e) =>
                          setEditedProfile({
                            ...editedProfile,
                            name: e.target.value,
                          })
                        }
                        style={
                          !profileEditMode ? { background: "#f8f9fa" } : {}
                        }
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label fw-bold">Email</label>
                      <input
                        type="email"
                        className="form-control"
                        value={
                          profileEditMode
                            ? editedProfile.email
                            : userData?.email || ""
                        }
                        readOnly={!profileEditMode}
                        onChange={(e) =>
                          setEditedProfile({
                            ...editedProfile,
                            email: e.target.value,
                          })
                        }
                        style={
                          !profileEditMode ? { background: "#f8f9fa" } : {}
                        }
                      />
                    </div>
                  </div>
                  <div className="row mb-3">
                    <div className="col-md-6">
                      <label className="form-label fw-bold">Phone</label>
                      <input
                        type="text"
                        className="form-control"
                        value={
                          profileEditMode
                            ? editedProfile.phone
                            : userData?.phone || ""
                        }
                        readOnly={!profileEditMode}
                        onChange={(e) =>
                          setEditedProfile({
                            ...editedProfile,
                            phone: e.target.value,
                          })
                        }
                        style={
                          !profileEditMode ? { background: "#f8f9fa" } : {}
                        }
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label fw-bold">City</label>
                      <input
                        type="text"
                        className="form-control"
                        value={
                          profileEditMode
                            ? editedProfile.city
                            : userData?.city || ""
                        }
                        readOnly={!profileEditMode}
                        onChange={(e) =>
                          setEditedProfile({
                            ...editedProfile,
                            city: e.target.value,
                          })
                        }
                        style={
                          !profileEditMode ? { background: "#f8f9fa" } : {}
                        }
                      />
                    </div>
                  </div>
                  <div className="alert alert-info">
                    <i className="fas fa-info-circle me-2"></i>Status:{" "}
                    <strong>✓ Approved & Active</strong>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* CASE DETAIL (unchanged) */}
          {activeView === "case-detail" && selectedCase && (
            <div className="row">
              <div className="col-lg-8">
                <div className="content-card mb-4">
                  <div className="card-title">
                    <span>
                      <i className="fas fa-info-circle me-2"></i>Case Overview
                    </span>
                    <button
                      style={{
                        background: "transparent",
                        border: "1px solid var(--primary)",
                        color: "var(--primary)",
                        padding: "6px 15px",
                        borderRadius: "6px",
                        cursor: "pointer",
                      }}
                      onClick={() => setActiveView("my-cases")}
                    >
                      <i className="fas fa-arrow-left me-2"></i>Back
                    </button>
                  </div>
                  <div className="row mb-4">
                    <div className="col-md-6">
                      <h5 style={{ color: "var(--primary)" }}>
                        {selectedCase.title}
                      </h5>
                      <div>
                        <strong>Type:</strong> {selectedCase.case_type || "—"}
                      </div>
                      <div>
                        <strong>Urgency:</strong>{" "}
                        {selectedCase.urgency || "Normal"}
                      </div>
                      {selectedCase.estimated_value && (
                        <div>
                          <strong>Value:</strong> ₹
                          {selectedCase.estimated_value}
                        </div>
                      )}
                    </div>
                    <div className="col-md-6">
                      <div>
                        <strong>Case ID:</strong> #{selectedCase.id}
                      </div>
                      <div>
                        <strong>Created:</strong>{" "}
                        {formatDate(selectedCase.created_at)}
                      </div>
                      <div>
                        <strong>Status:</strong>{" "}
                        <span
                          className={`case-status ${getStatusBadgeClass(selectedCase.status)}`}
                        >
                          {getStatusText(selectedCase.status)}
                        </span>
                      </div>
                    </div>
                  </div>
                  {selectedCase.description && (
                    <>
                      <h6>Description</h6>
                      <p>{selectedCase.description}</p>
                    </>
                  )}
                  {selectedCase.court_location && (
                    <div>
                      <strong>Court:</strong> {selectedCase.court_location}
                    </div>
                  )}
                  {selectedCase.opposing_party && (
                    <div>
                      <strong>Opposing Party:</strong>{" "}
                      {selectedCase.opposing_party}
                    </div>
                  )}
                  {selectedCase.preferred_outcome && (
                    <div className="mt-2">
                      <strong>Preferred Outcome:</strong>
                      <p>{selectedCase.preferred_outcome}</p>
                    </div>
                  )}
                </div>
              </div>
              <div className="col-lg-4">
                <div className="content-card mb-4">
                  <h6 className="card-title">
                    <i className="fas fa-file-upload me-2"></i>Documents
                  </h6>
                  {selectedCase.documents?.length > 0 ? (
                    selectedCase.documents.map((doc) => (
                      <div
                        key={doc.id}
                        style={{
                          padding: "8px 0",
                          borderBottom: "1px solid #e9ecef",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <span>
                          <i
                            className="fas fa-file-pdf me-2"
                            style={{ color: "#dc3545" }}
                          ></i>
                          {doc.file_name || doc.name}
                        </span>
                        {(doc.file_url || doc.file) && (
                          <button
                            className="btn btn-sm btn-link"
                            onClick={() =>
                              window.open(doc.file_url || doc.file)
                            }
                          >
                            Download
                          </button>
                        )}
                      </div>
                    ))
                  ) : (
                    <p>No documents uploaded yet.</p>
                  )}
                  <button
                    className="btn-advocare w-100 mt-3"
                    onClick={() => {
                      setSelectedDocCase(selectedCase);
                      setShowDocModal(true);
                    }}
                  >
                    <i className="fas fa-upload me-2"></i>Upload Document
                  </button>
                </div>
                <div className="content-card">
                  <h6 className="card-title">
                    <i className="fas fa-user-tie me-2"></i>Assigned Law Firm
                  </h6>
                  {selectedCase.law_firm_name || selectedCase.law_firm ? (
                    <>
                      <p
                        style={{
                          fontWeight: "600",
                          color: "var(--primary)",
                          textAlign: "center",
                        }}
                      >
                        {selectedCase.law_firm_name || "Law Firm"}
                      </p>
                      <button
                        className="btn-advocare w-100"
                        onClick={() =>
                          openChat(selectedCase, {
                            firm_name: selectedCase.law_firm_name,
                            id:
                              selectedCase.law_firm_id || selectedCase.law_firm,
                          })
                        }
                      >
                        <i className="fas fa-comment me-2"></i>Contact Law Firm
                      </button>
                    </>
                  ) : (
                    <>
                      <p style={{ textAlign: "center", color: "#6c757d" }}>
                        Not assigned yet
                      </p>
                      <button
                        className="btn-advocare w-100"
                        onClick={() => {
                          setActiveView("find-lawfirm");
                          setShowAISection(true);
                        }}
                      >
                        <i className="fas fa-robot me-2"></i>Find with AI Match
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* FILTER MODAL (unchanged) */}
      {showFilterModal && (
        <div
          className="modal-overlay"
          onClick={() => setShowFilterModal(false)}
        >
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                <i className="fas fa-sliders-h me-2"></i>Advanced Filters
              </h3>
              <button
                className="modal-close"
                onClick={() => setShowFilterModal(false)}
              >
                &times;
              </button>
            </div>
            <div style={{ padding: "25px" }}>
              {[
                ["specialization", "Specialization", "e.g., Criminal, Civil"],
                ["location", "Location", "City or area"],
                ["language", "Language", "e.g., Hindi, English, Gujarati"],
              ].map(([k, l, ph]) => (
                <div key={k} className="form-group mb-3">
                  <label className="fw-bold">{l}</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder={ph}
                    value={searchFilters[k]}
                    onChange={(e) =>
                      setSearchFilters({
                        ...searchFilters,
                        [k]: e.target.value,
                      })
                    }
                  />
                </div>
              ))}
              <div className="form-group mb-3">
                <label className="fw-bold">Min Experience (Years)</label>
                <input
                  type="number"
                  className="form-control"
                  placeholder="Years"
                  value={searchFilters.experience}
                  onChange={(e) =>
                    setSearchFilters({
                      ...searchFilters,
                      experience: e.target.value,
                    })
                  }
                />
              </div>
              <div className="form-group mb-3">
                <label className="fw-bold">Minimum Rating</label>
                <select
                  className="form-control"
                  value={searchFilters.rating}
                  onChange={(e) =>
                    setSearchFilters({
                      ...searchFilters,
                      rating: e.target.value,
                    })
                  }
                >
                  <option value="">Any Rating</option>
                  <option value="4.5">4.5+ Stars</option>
                  <option value="4.0">4.0+ Stars</option>
                  <option value="3.5">3.5+ Stars</option>
                </select>
              </div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "12px",
                }}
              >
                <button
                  onClick={() =>
                    setSearchFilters({
                      specialization: "",
                      location: "",
                      experience: "",
                      rating: "",
                      language: "",
                    })
                  }
                  style={{
                    padding: "10px 20px",
                    borderRadius: "6px",
                    border: "none",
                    cursor: "pointer",
                    background: "#6c757d",
                    color: "white",
                  }}
                >
                  Clear All
                </button>
                <button
                  onClick={() => setShowFilterModal(false)}
                  style={{
                    padding: "10px 20px",
                    borderRadius: "6px",
                    border: "none",
                    cursor: "pointer",
                    background: "var(--primary)",
                    color: "white",
                  }}
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* UPLOAD DOC MODAL (improved) */}
      {showDocModal && (
        <div className="modal-overlay" onClick={() => setShowDocModal(false)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                <i className="fas fa-upload me-2"></i>Upload Document
              </h3>
              <button
                className="modal-close"
                onClick={() => setShowDocModal(false)}
              >
                &times;
              </button>
            </div>
            <div style={{ padding: "25px" }}>
              <p>
                Case: <strong>{selectedDocCase?.title}</strong>
              </p>
              <div className="form-group mb-3">
                <label className="fw-bold">Document Type</label>
                <select
                  className="form-control"
                  value={selectedDocType}
                  onChange={(e) => setSelectedDocType(e.target.value)}
                >
                  <option value="fir">FIR Document</option>
                  <option value="notice">Notice / Agreement</option>
                  <option value="evidence">Evidence Document</option>
                  <option value="correspondence">Correspondence</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="form-group mb-3">
                <label className="fw-bold">Select File</label>
                <input
                  type="file"
                  className="form-control"
                  accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                />
                <small>PDF, JPG, PNG, DOC, DOCX (Max 10MB)</small>
              </div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "12px",
                  paddingTop: "15px",
                  borderTop: "1px solid #e9ecef",
                }}
              >
                <button
                  onClick={() => {
                    setShowDocModal(false);
                    setSelectedFile(null);
                  }}
                  style={{
                    padding: "10px 20px",
                    borderRadius: "6px",
                    border: "none",
                    cursor: "pointer",
                    background: "#6c757d",
                    color: "white",
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={uploadDocument}
                  disabled={!selectedFile || uploadingDoc}
                  style={{
                    padding: "10px 20px",
                    borderRadius: "6px",
                    border: "none",
                    cursor:
                      !selectedFile || uploadingDoc ? "not-allowed" : "pointer",
                    background: "var(--primary)",
                    color: "white",
                    opacity: !selectedFile || uploadingDoc ? 0.6 : 1,
                  }}
                >
                  {uploadingDoc ? (
                    <>
                      <i className="fas fa-spinner fa-spin me-2"></i>
                      Uploading...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-upload me-2"></i>Upload
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ClientPortal;