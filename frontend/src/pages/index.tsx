import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export default function Home() {
  // States
  const [cvAnalysis, setCvAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');
  const [jobs, setJobs] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [matchResult, setMatchResult] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [interviewPrep, setInterviewPrep] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  
  // Simulation states
  const [simulation, setSimulation] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [scores, setScores] = useState([]);
  const [finalResult, setFinalResult] = useState(null);
  const [isSimulationActive, setIsSimulationActive] = useState(false);

  // Dropzone
  const onDrop = useCallback(async (files) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', files[0]);
    
    try {
      const response = await axios.post(`${API_URL}/analyze-cv`, formData);
      setCvAnalysis(response.data);
      setActiveTab('results');
    } catch (error) {
      console.error('Error:', error);
      alert('Error analyzing CV');
    }
    setLoading(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop, 
    accept: { 
      'application/pdf': ['.pdf'], 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] 
    }
  });

  // Job functions
  const searchJobs = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/search-jobs`, { 
        params: { query: searchQuery } 
      });
      setJobs(response.data.jobs);
      setActiveTab('jobs');
    } catch (error) {
      console.error('Error:', error);
      alert('Error searching jobs');
    }
    setLoading(false);
  };

  const matchWithJob = async (job) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/match-job`, job);
      setMatchResult(response.data);
      setSelectedJob(job);
    } catch (error) {
      console.error('Error:', error);
      alert('Error matching with job');
    }
    setLoading(false);
  };

  // Interview functions
  const prepareInterview = async () => {
    if (!selectedJob) {
      alert('Please select a job first');
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/prepare-interview`, {
        title: selectedJob.title,
        description: selectedJob.description,
        company: selectedJob.company
      });
      setInterviewPrep(response.data);
      setActiveTab('interview');
    } catch (error) {
      console.error('Error:', error);
      alert('Error preparing interview');
    }
    setLoading(false);
  };

  // Simulation functions
  const startSimulation = async () => {
    if (!selectedJob) {
      alert('Please select a job first');
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/start-simulated-interview`, {
        title: selectedJob.title,
        description: selectedJob.description,
        company: selectedJob.company
      });
      setSimulation(response.data);
      setIsSimulationActive(true);
      setCurrentQuestionIndex(0);
      setUserAnswers({});
      setScores([]);
      setFinalResult(null);
    } catch (error) {
      console.error('Error:', error);
      alert('Error starting simulation');
    }
    setLoading(false);
  };

  const submitAnswer = async (questionId, question, expectedAnswer, pointsMax) => {
    const answer = userAnswers[questionId];
    if (!answer || !answer.trim()) {
      alert('Please write your answer');
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/evaluate-answer`, {
        question: question,
        user_answer: answer,
        expected_answer: expectedAnswer,
        points_max: pointsMax
      });
      
      const newScores = [...scores, response.data.score];
      setScores(newScores);
      
      if (currentQuestionIndex + 1 < simulation.questions.length) {
        setCurrentQuestionIndex(prev => prev + 1);
      } else {
        const finalResponse = await axios.post(`${API_URL}/final-decision`, {
          scores: newScores,
          total_max: simulation.total_points_max,
          job_title: simulation.job_title
        });
        setFinalResult(finalResponse.data);
        setIsSimulationActive(false);
      }
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  // Career functions
  const generateRoadmap = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/career-roadmap`, null, {
        params: { target_role: 'Senior Software Engineer' }
      });
      setRoadmap(response.data);
      setActiveTab('career');
    } catch (error) {
      console.error('Error:', error);
      alert('Error generating roadmap');
    }
    setLoading(false);
  };

  // Styles
  const styles = {
    container: { minHeight: '100vh', background: '#f5f7fa' },
    header: { background: 'white', borderBottom: '1px solid #e0e4e8', padding: '16px 24px', position: 'sticky' as const, top: 0, zIndex: 50 },
    headerInner: { maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' as const, gap: '16px' },
    logo: { fontWeight: 'bold', fontSize: '20px', color: '#1a1a2e' },
    nav: { display: 'flex', gap: '4px', flexWrap: 'wrap' as const },
    navButton: (active: boolean) => ({ 
      padding: '8px 16px', 
      background: active ? '#1a1a2e' : 'transparent', 
      color: active ? 'white' : '#4a5568',
      border: 'none',
      borderRadius: '8px',
      cursor: 'pointer',
      fontWeight: active ? 600 : 400,
      fontSize: '13px',
      transition: 'all 0.2s'
    }),
    main: { maxWidth: '1000px', margin: '0 auto', padding: '40px 24px' },
    title: { fontSize: '32px', fontWeight: 'bold', marginBottom: '12px', textAlign: 'center' as const, color: '#1a1a2e' },
    subtitle: { color: '#6b7280', textAlign: 'center' as const, marginBottom: '48px' },
    dropzone: { 
      background: 'white', 
      borderRadius: '20px', 
      padding: '60px', 
      textAlign: 'center' as const, 
      cursor: 'pointer',
      border: `2px dashed ${isDragActive ? '#1a1a2e' : '#d1d5db'}`,
      transition: 'all 0.3s'
    },
    dropzoneTitle: { fontWeight: 500, marginBottom: '8px', fontSize: '18px' },
    dropzoneText: { color: '#9ca3af', fontSize: '14px', marginBottom: '16px' },
    dropzoneFormats: { display: 'flex', justifyContent: 'center', gap: '16px', fontSize: '12px', color: '#9ca3af' },
    scoreGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '32px' },
    scoreCard: { background: 'white', borderRadius: '16px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' },
    scoreValue: { fontSize: '28px', fontWeight: 'bold', color: '#1a1a2e' },
    scoreLabel: { color: '#6b7280', fontSize: '13px', marginTop: '4px' },
    card: { background: 'white', borderRadius: '16px', padding: '24px', marginBottom: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' },
    cardTitle: { fontWeight: 'bold', marginBottom: '16px', fontSize: '16px', color: '#1a1a2e' },
    listItem: { padding: '8px 0', borderBottom: '1px solid #f0f0f0', color: '#4a5568' },
    keywordContainer: { display: 'flex', flexWrap: 'wrap' as const, gap: '8px' },
    keyword: { padding: '6px 12px', background: '#f3f4f6', borderRadius: '20px', fontSize: '12px', color: '#4a5568' },
    searchContainer: { display: 'flex', gap: '12px', marginBottom: '32px' },
    searchInput: { flex: 1, padding: '12px 20px', border: '1px solid #d1d5db', borderRadius: '12px', outline: 'none', fontSize: '14px' },
    searchButton: { background: '#1a1a2e', color: 'white', padding: '12px 28px', borderRadius: '12px', border: 'none', cursor: 'pointer', fontWeight: 500 },
    jobCard: { background: 'white', borderRadius: '12px', padding: '20px', marginBottom: '12px', cursor: 'pointer', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', border: '1px solid #e5e7eb' },
    jobTitle: { fontWeight: 600, fontSize: '16px', marginBottom: '4px', color: '#1a1a2e' },
    jobCompany: { color: '#6b7280', fontSize: '13px', marginBottom: '8px' },
    skillBadge: { padding: '4px 10px', background: '#f3f4f6', borderRadius: '12px', fontSize: '11px', marginRight: '6px', display: 'inline-block', color: '#4a5568' },
    footer: { borderTop: '1px solid #e0e4e8', padding: '24px', textAlign: 'center' as const, fontSize: '12px', color: '#9ca3af' },
    modal: { position: 'fixed' as const, top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
    modalContent: { background: 'white', borderRadius: '20px', maxWidth: '450px', width: '90%', padding: '32px', textAlign: 'center' as const },
    modalScore: { fontSize: '48px', fontWeight: 'bold', margin: '16px 0', color: '#1a1a2e' },
    loadingOverlay: { position: 'fixed' as const, top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(255,255,255,0.9)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
    spinner: { width: '40px', height: '40px', border: '2px solid #e0e4e8', borderTopColor: '#1a1a2e', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 16px' },
    questionCard: { background: '#f8f9fa', borderRadius: '12px', padding: '16px', marginBottom: '16px' },
    questionTitle: { fontWeight: 600, marginBottom: '8px', color: '#1a1a2e' },
    answerText: { color: '#6b7280', fontSize: '13px', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #e5e7eb' },
    roadmapText: { whiteSpace: 'pre-wrap' as const, lineHeight: 1.6, color: '#4a5568' },
    textarea: { width: '100%', padding: '12px', border: '1px solid #d1d5db', borderRadius: '12px', fontSize: '14px', fontFamily: 'inherit', resize: 'vertical' as const }
  };

  const scores_data = cvAnalysis ? [
    { label: 'CV Score', value: cvAnalysis.cv_score || 0 },
    { label: 'ATS Score', value: cvAnalysis.ats_compatibility || 0 },
    { label: 'Skill Match', value: cvAnalysis.skill_relevance || 0 },
    { label: 'Employability', value: cvAnalysis.employability_score || 0 }
  ] : [];

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerInner}>
          <span style={styles.logo}>Job-Miner</span>
          <div style={styles.nav}>
            <button style={styles.navButton(activeTab === 'upload')} onClick={() => setActiveTab('upload')}>Upload</button>
            <button style={styles.navButton(activeTab === 'results')} onClick={() => setActiveTab('results')}>Analysis</button>
            <button style={styles.navButton(activeTab === 'jobs')} onClick={() => setActiveTab('jobs')}>Jobs</button>
            <button style={styles.navButton(activeTab === 'interview')} onClick={() => setActiveTab('interview')}>Interview</button>
            <button style={styles.navButton(activeTab === 'simulator')} onClick={() => setActiveTab('simulator')}>Simulator</button>
            <button style={styles.navButton(activeTab === 'career')} onClick={() => setActiveTab('career')}>Career</button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={styles.main}>
        {/* ============ UPLOAD TAB ============ */}
        {activeTab === 'upload' && (
          <div>
            <h1 style={styles.title}>Analyze your CV</h1>
            <p style={styles.subtitle}>Get AI-powered insights to optimize your job search</p>
            
            <div {...getRootProps()} style={styles.dropzone}>
              <input {...getInputProps()} />
              <div style={styles.dropzoneTitle}>{isDragActive ? 'Drop your CV here' : 'Drag and drop your CV'}</div>
              <p style={styles.dropzoneText}>or click to browse</p>
              <div style={styles.dropzoneFormats}>
                <span>PDF</span>
                <span>DOCX</span>
                <span>Max 10MB</span>
              </div>
            </div>
          </div>
        )}

        {/* ============ RESULTS TAB ============ */}
        {activeTab === 'results' && cvAnalysis && (
          <div>
            <h1 style={{ ...styles.title, textAlign: 'left', marginBottom: '24px' }}>Your Analysis</h1>
            
            <div style={styles.scoreGrid}>
              {scores_data.map((stat, i) => (
                <div key={i} style={styles.scoreCard}>
                  <div style={styles.scoreValue}>{stat.value}%</div>
                  <div style={styles.scoreLabel}>{stat.label}</div>
                </div>
              ))}
            </div>

            <div style={styles.card}>
              <div style={styles.cardTitle}>Strengths</div>
              {(cvAnalysis.strengths || ['Professional experience', 'Technical skills', 'Education']).slice(0, 4).map((s: string, i: number) => (
                <div key={i} style={styles.listItem}>{s}</div>
              ))}
            </div>

            <div style={styles.card}>
              <div style={styles.cardTitle}>Areas to Improve</div>
              {(cvAnalysis.weaknesses || ['Add more metrics', 'Highlight achievements', 'Improve formatting']).slice(0, 3).map((w: string, i: number) => (
                <div key={i} style={styles.listItem}>{w}</div>
              ))}
            </div>

            <div style={styles.card}>
              <div style={styles.cardTitle}>Recommended Keywords</div>
              <div style={styles.keywordContainer}>
                {(cvAnalysis.missing_keywords || ['Python', 'React', 'SQL', 'Git', 'Docker']).slice(0, 10).map((kw: string, i: number) => (
                  <span key={i} style={styles.keyword}>{kw}</span>
                ))}
              </div>
            </div>

            <button onClick={generateRoadmap} style={{ ...styles.searchButton, width: '100%' }}>
              Generate Career Roadmap
            </button>
          </div>
        )}

        {/* ============ JOBS TAB ============ */}
        {activeTab === 'jobs' && (
          <div>
            <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px', color: '#1a1a2e' }}>Opportunities</h1>
            <p style={{ color: '#6b7280', marginBottom: '32px' }}>Find roles that match your skills</p>
            
            <div style={styles.searchContainer}>
              <input 
                type="text" 
                placeholder="Search by title, skills, or company..." 
                style={styles.searchInput}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && searchJobs()}
              />
              <button style={styles.searchButton} onClick={searchJobs}>Search</button>
            </div>

            {jobs.length === 0 && !searchQuery && (
              <div style={styles.card}>
                <p style={{ textAlign: 'center', color: '#6b7280' }}>
                  Enter a search term like "Python", "React", or "DevOps" to see job opportunities
                </p>
              </div>
            )}

            {jobs.length === 0 && searchQuery && (
              <div style={{ textAlign: 'center', padding: '48px', color: '#9ca3af' }}>
                No results found for "{searchQuery}". Try another search.
              </div>
            )}

            {jobs.map((job: any, i: number) => (
              <div key={i} style={styles.jobCard} onClick={() => matchWithJob(job)}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={styles.jobTitle}>{job.title}</div>
                    <div style={styles.jobCompany}>{job.company} - {job.location}</div>
                    <div style={{ fontSize: '12px', color: '#9ca3af', margin: '8px 0' }}>
                      {job.salary_range} - {job.experience_level}
                    </div>
                    <div style={{ marginTop: '8px' }}>
                      {(job.requirements?.skills || []).slice(0, 5).map((skill: string, idx: number) => (
                        <span key={idx} style={styles.skillBadge}>{skill}</span>
                      ))}
                    </div>
                  </div>
                  <button style={{ ...styles.searchButton, padding: '8px 16px', fontSize: '12px', marginLeft: '16px' }}>
                    Match
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ============ INTERVIEW TAB ============ */}
        {activeTab === 'interview' && (
          <div>
            <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px', color: '#1a1a2e' }}>Interview Preparation</h1>
            <p style={{ color: '#6b7280', marginBottom: '32px' }}>AI-powered questions based on your profile</p>

            {!interviewPrep ? (
              <div style={styles.card}>
                <p style={{ marginBottom: '16px', color: '#6b7280' }}>Select a job first to generate interview questions</p>
                <button onClick={() => setActiveTab('jobs')} style={styles.searchButton}>
                  Browse Jobs
                </button>
              </div>
            ) : (
              <div>
                <div style={{ ...styles.card, background: '#f0fdf4' }}>
                  <div style={styles.cardTitle}>Interview Tips</div>
                  <ul style={{ marginLeft: '20px', color: '#4a5568' }}>
                    <li>Use the STAR method for behavioral questions</li>
                    <li>Research the company before the interview</li>
                    <li>Prepare questions to ask at the end</li>
                    <li>Practice answering out loud</li>
                  </ul>
                </div>

                {interviewPrep.questions?.technical?.length > 0 && (
                  <div style={styles.card}>
                    <div style={styles.cardTitle}>Technical Questions</div>
                    {interviewPrep.questions.technical.map((q: string, i: number) => (
                      <div key={i} style={styles.questionCard}>
                        <div style={styles.questionTitle}>{q}</div>
                      </div>
                    ))}
                  </div>
                )}

                {interviewPrep.questions?.hr?.length > 0 && (
                  <div style={styles.card}>
                    <div style={styles.cardTitle}>HR Questions</div>
                    {interviewPrep.questions.hr.map((q: string, i: number) => (
                      <div key={i} style={styles.questionCard}>
                        <div style={styles.questionTitle}>{q}</div>
                      </div>
                    ))}
                  </div>
                )}

                {interviewPrep.questions?.behavioral?.length > 0 && (
                  <div style={styles.card}>
                    <div style={styles.cardTitle}>Behavioral Questions</div>
                    {interviewPrep.questions.behavioral.map((q: string, i: number) => (
                      <div key={i} style={styles.questionCard}>
                        <div style={styles.questionTitle}>{q}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ============ SIMULATOR TAB ============ */}
        {activeTab === 'simulator' && (
          <div>
            <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px', color: '#1a1a2e' }}>Interview Simulator</h1>
            <p style={{ color: '#6b7280', marginBottom: '32px' }}>Practice with AI and get a final decision</p>

            {!selectedJob && !simulation && (
              <div style={styles.card}>
                <p style={{ marginBottom: '16px', color: '#6b7280' }}>Select a job first to start the interview simulation</p>
                <button onClick={() => setActiveTab('jobs')} style={styles.searchButton}>
                  Browse Jobs
                </button>
              </div>
            )}

            {selectedJob && !simulation && !isSimulationActive && (
              <div style={styles.card}>
                <div style={styles.cardTitle}>Job: {selectedJob.title} at {selectedJob.company}</div>
                <p style={{ marginBottom: '16px', color: '#6b7280' }}>The AI will ask you 5 questions and evaluate your answers.</p>
                <button onClick={startSimulation} style={styles.searchButton}>
                  Start Simulated Interview
                </button>
              </div>
            )}

            {isSimulationActive && simulation && (
              <div style={styles.card}>
                <div style={{ marginBottom: '16px' }}>
                  <span style={{ background: '#1a1a2e', color: 'white', padding: '4px 12px', borderRadius: '20px', fontSize: '12px' }}>
                    Question {currentQuestionIndex + 1} / {simulation.questions.length}
                  </span>
                </div>
                <div style={styles.questionCard}>
                  <div style={styles.questionTitle}>{simulation.questions[currentQuestionIndex].question}</div>
                  <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '8px' }}>
                    Type: {simulation.questions[currentQuestionIndex].type} | Points: {simulation.questions[currentQuestionIndex].points_max}
                  </div>
                  <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #e5e7eb' }}>
                    <strong>Expected points:</strong> {simulation.questions[currentQuestionIndex].expected_answer}
                  </div>
                </div>
                
                <textarea
                  rows={5}
                  style={styles.textarea}
                  placeholder="Write your answer here..."
                  value={userAnswers[simulation.questions[currentQuestionIndex].id] || ''}
                  onChange={(e) => setUserAnswers(prev => ({
                    ...prev,
                    [simulation.questions[currentQuestionIndex].id]: e.target.value
                  }))}
                />
                
                <button 
                  onClick={() => submitAnswer(
                    simulation.questions[currentQuestionIndex].id,
                    simulation.questions[currentQuestionIndex].question,
                    simulation.questions[currentQuestionIndex].expected_answer,
                    simulation.questions[currentQuestionIndex].points_max
                  )}
                  style={{ ...styles.searchButton, marginTop: '16px', width: '100%' }}
                >
                  Submit Answer
                </button>
              </div>
            )}

            {finalResult && (
              <div style={styles.card}>
                <div style={styles.cardTitle}>Final Decision</div>
                <div style={{ textAlign: 'center', margin: '24px 0' }}>
                  <div style={{ 
                    fontSize: '48px', 
                    fontWeight: 'bold',
                    color: finalResult.color === 'green' ? '#2b6e3c' : 
                           finalResult.color === 'orange' ? '#b45b0a' :
                           finalResult.color === 'yellow' ? '#b45b0a' : '#c53030'
                  }}>
                    {finalResult.final_decision}
                  </div>
                  <div style={{ fontSize: '24px', marginTop: '8px' }}>
                    Score: {finalResult.total_score}/{finalResult.total_max} ({finalResult.percentage}%)
                  </div>
                  <p style={{ color: '#6b7280', marginTop: '16px' }}>{finalResult.message}</p>
                </div>
                
                <div style={{ marginTop: '24px' }}>
                  <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Recommendations:</div>
                  <ul style={{ marginLeft: '20px', color: '#4a5568' }}>
                    {finalResult.recommendations.map((rec: string, i: number) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>

                <button 
                  onClick={() => {
                    setSimulation(null);
                    setFinalResult(null);
                    setSelectedJob(null);
                    setUserAnswers({});
                    setScores([]);
                  }}
                  style={{ ...styles.searchButton, marginTop: '24px', width: '100%', background: '#e5e7eb', color: '#1a1a2e' }}
                >
                  Try Another Interview
                </button>
              </div>
            )}
          </div>
        )}

        {/* ============ CAREER TAB ============ */}
        {activeTab === 'career' && (
          <div>
            <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px', color: '#1a1a2e' }}>Career Development</h1>
            <p style={{ color: '#6b7280', marginBottom: '32px' }}>Personalized roadmap to achieve your goals</p>

            {!roadmap ? (
              <div style={styles.card}>
                <p style={{ marginBottom: '16px', color: '#6b7280' }}>Generate a personalized career roadmap based on your CV</p>
                <button onClick={generateRoadmap} style={styles.searchButton}>
                  Generate Roadmap
                </button>
              </div>
            ) : (
              <div>
                <div style={styles.card}>
                  <div style={styles.cardTitle}>Career Roadmap</div>
                  <div style={styles.roadmapText}>{roadmap.roadmap}</div>
                </div>

                {roadmap.recommended_certifications?.length > 0 && (
                  <div style={styles.card}>
                    <div style={styles.cardTitle}>Recommended Certifications</div>
                    {roadmap.recommended_certifications.map((cert: any, i: number) => (
                      <div key={i} style={{ ...styles.listItem, display: 'flex', justifyContent: 'space-between' }}>
                        <span>{cert.certification}</span>
                        <span style={{ fontSize: '12px', color: '#9ca3af' }}>{cert.estimated_time}</span>
                      </div>
                    ))}
                  </div>
                )}

                {roadmap.recommended_courses?.length > 0 && (
                  <div style={styles.card}>
                    <div style={styles.cardTitle}>Recommended Courses</div>
                    {roadmap.recommended_courses.map((course: any, i: number) => (
                      <div key={i} style={styles.listItem}>
                        {course.course} - {course.platform}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={styles.footer}>
        <span>Job-Miner - AI Career Platform</span>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div style={styles.loadingOverlay}>
          <div style={{ textAlign: 'center' }}>
            <div style={styles.spinner}></div>
            <p>Loading...</p>
          </div>
        </div>
      )}

      {/* Match Modal */}
      {matchResult && selectedJob && (
        <div style={styles.modal} onClick={() => setMatchResult(null)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '16px' }}>Match Analysis</div>
            <div style={styles.modalScore}>{matchResult.match_percentage}%</div>
            <p style={{ color: '#6b7280', marginBottom: '24px' }}>Match Score</p>
            
            {matchResult.missing_skills?.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <div style={{ fontWeight: 500, marginBottom: '8px' }}>Missing skills:</div>
                <div style={styles.keywordContainer}>
                  {matchResult.missing_skills.slice(0, 5).map((skill: string, i: number) => (
                    <span key={i} style={styles.keyword}>{skill}</span>
                  ))}
                </div>
              </div>
            )}
            
            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={() => setMatchResult(null)} style={{ ...styles.searchButton, background: '#e5e7eb', color: '#1a1a2e' }}>
                Close
              </button>
              <button onClick={prepareInterview} style={styles.searchButton}>
                Prepare Interview
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}