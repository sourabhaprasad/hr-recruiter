"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Upload, User, CheckCircle, AlertCircle } from "lucide-react";
import Link from "next/link";

interface JobTitle {
  id: number;
  title: string;
}

export default function UploadResumePage() {
  const [resume, setResume] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [gender, setGender] = useState("");
  const [selectedJobId, setSelectedJobId] = useState("");
  const [jobTitles, setJobTitles] = useState<JobTitle[]>([]);
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchJobTitles();
  }, []);

  const fetchJobTitles = async () => {
    try {
      const response = await fetch("http://localhost:8000/jd/titles/list");
      if (response.ok) {
        const titles = await response.json();
        setJobTitles(titles);
      }
    } catch (error) {
      console.error("Error fetching job titles:", error);
    }
  };

  const handleFileUpload = async (file: File) => {
    setResume(file);
    setExtracting(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/resume/extract", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const extractedData = await response.json();
        
        // Auto-fill form fields with extracted data - always override if extracted
        if (extractedData.name) setName(extractedData.name);
        if (extractedData.email) setEmail(extractedData.email);
        if (extractedData.phone) setPhone(extractedData.phone);
        
        console.log("Extracted data:", extractedData); // Debug log
      }
    } catch (error) {
      console.error("Error extracting resume details:", error);
    } finally {
      setExtracting(false);
    }
  };

  const handleSubmit = async () => {
    if (!name.trim()) {
      setError("Candidate name is required");
      return;
    }

    if (!resume) {
      setError("Please upload a resume file");
      return;
    }

    if (!selectedJobId) {
      setError("Please select a job position");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("name", name);
      formData.append("file", resume);
      formData.append("jd_id", selectedJobId);
      
      if (email) formData.append("email", email);
      if (phone) formData.append("phone", phone);
      if (gender) formData.append("gender", gender);

      const response = await fetch("http://localhost:8000/resume/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload resume");
      }

      const data = await response.json();
      setResult(data);
      
      // Reset form
      setResume(null);
      setName("");
      setEmail("");
      setPhone("");
      setGender("");
      setSelectedJobId("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <Link href="/" className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Link>
          
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-600">
                <CheckCircle className="h-6 w-6" />
                Resume Uploaded Successfully!
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Upload Summary:</h3>
                <p><strong>Candidate ID:</strong> {result.candidate_id}</p>
                <p><strong>Job Matches Created:</strong> {result.matches_created}</p>
              </div>
              
              {result.extracted_data && (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-2">Extracted Information:</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p><strong>Email:</strong> {result.extracted_data.email || "Not found"}</p>
                        <p><strong>Phone:</strong> {result.extracted_data.phone || "Not found"}</p>
                      </div>
                      <div>
                        <p><strong>Experience:</strong> {result.extracted_data.experience_years ? `${result.extracted_data.experience_years} years` : "Not found"}</p>
                        <p><strong>Education:</strong> {result.extracted_data.education || "Not found"}</p>
                      </div>
                    </div>
                  </div>
                  
                  {result.extracted_data.skills && result.extracted_data.skills.length > 0 && (
                    <div>
                      <h3 className="font-semibold mb-2">Extracted Skills:</h3>
                      <div className="flex flex-wrap gap-2">
                        {result.extracted_data.skills.map((skill: string, index: number) => (
                          <Badge key={index} variant="secondary">{skill}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              <div className="flex gap-2">
                <Link href="/dashboard">
                  <Button>View Dashboard</Button>
                </Link>
                <Button variant="outline" onClick={() => setResult(null)}>
                  Upload Another Resume
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <Link href="/" className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-6">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Link>
        
        <Card className="max-w-2xl mx-auto shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-6 w-6 text-green-600" />
              Upload Resume
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
                <AlertCircle className="h-4 w-4" />
                {error}
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium mb-2">Job Position *</label>
              <select
                value={selectedJobId}
                onChange={(e) => setSelectedJobId(e.target.value)}
                className="w-full h-10 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a job position</option>
                {jobTitles.map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.title}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Candidate Name *</label>
                <Input
                  placeholder="Full Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <Input
                  type="email"
                  placeholder="email@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Phone</label>
                <Input
                  placeholder="+1 (555) 123-4567"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Gender (Optional)</label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="w-full h-10 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                  <option value="prefer-not-to-say">Prefer not to say</option>
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Resume File *</label>
              <label htmlFor="resume-upload" className="cursor-pointer">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    {resume ? resume.name : "Upload Resume"}
                  </p>
                  <p className="text-sm text-gray-600">
                    Drag and drop or click to select PDF, DOC, or DOCX files
                  </p>
                  {extracting && (
                    <div className="mt-4 flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                      <span className="text-sm text-blue-600">Extracting details...</span>
                    </div>
                  )}
                </div>
              </label>
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileUpload(file);
                }}
                className="hidden"
                id="resume-upload"
              />
            </div>
            
            <Button 
              onClick={handleSubmit} 
              disabled={loading || extracting}
              className="w-full bg-green-600 hover:bg-green-700"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processing...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Resume
                </>
              )}
            </Button>
            
            <div className="text-sm text-gray-600">
              <p><strong>Supported formats:</strong> PDF, DOC, DOCX</p>
              <p><strong>What happens next:</strong> We'll extract skills and experience, then automatically match against all job descriptions.</p>
              <p><strong>Privacy:</strong> Contact information is optional and used only for recruitment communications.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
