"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";
import Link from "next/link";

export default function UploadJDPage() {
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!title.trim()) {
      setError("Job title is required");
      return;
    }

    if (!jdFile && !jdText.trim()) {
      setError("Please upload a file or enter job description text");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("title", title);
      
      if (jdFile) {
        formData.append("file", jdFile);
      } else {
        formData.append("text", jdText);
      }

      const response = await fetch("http://localhost:8000/jd/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload job description");
      }

      const data = await response.json();
      setResult(data);
      
      // Reset form
      setJdFile(null);
      setJdText("");
      setTitle("");
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
                Job Description Uploaded Successfully!
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Upload Summary:</h3>
                <p><strong>JD ID:</strong> {result.jd_id}</p>
                <p><strong>Candidates Matched:</strong> {result.candidates_matched}</p>
              </div>
              
              {result.extracted_requirements && (
                <div>
                  <h3 className="font-semibold mb-2">Extracted Skills:</h3>
                  <div className="flex flex-wrap gap-2">
                    {result.extracted_requirements.required_skills?.map((skill: string, index: number) => (
                      <Badge key={index} variant="secondary">{skill}</Badge>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex gap-2">
                <Link href="/dashboard">
                  <Button>View Dashboard</Button>
                </Link>
                <Button variant="outline" onClick={() => setResult(null)}>
                  Upload Another JD
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
              <FileText className="h-6 w-6 text-blue-600" />
              Upload Job Description
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
              <label className="block text-sm font-medium mb-2">Job Title *</label>
              <Input
                placeholder="e.g., Senior Software Engineer"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Upload File</label>
              <Input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={(e) => setJdFile(e.target.files?.[0] || null)}
                className="w-full"
              />
              {jdFile && (
                <p className="text-sm text-gray-600 mt-1">
                  Selected: {jdFile.name}
                </p>
              )}
            </div>
            
            <div className="text-center text-gray-500 font-medium">OR</div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Paste Job Description</label>
              <Textarea
                placeholder="Paste the complete job description here..."
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                rows={8}
                className="w-full"
              />
            </div>
            
            <Button 
              onClick={handleSubmit} 
              className="w-full"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processing...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Job Description
                </>
              )}
            </Button>
            
            <div className="text-sm text-gray-600">
              <p><strong>Supported formats:</strong> PDF, DOC, DOCX, TXT</p>
              <p><strong>What happens next:</strong> We'll extract required skills and match against existing candidates automatically.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
