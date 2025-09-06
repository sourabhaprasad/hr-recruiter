import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, Users, BarChart3, Upload, UserCheck } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Talent Matcher
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            AI-powered recruitment platform with bias detection and skill matching
          </p>
          <div className="flex justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
                <BarChart3 className="mr-2 h-5 w-5" />
                View Dashboard
              </Button>
            </Link>
            <Link href="/upload-jd">
              <Button size="lg" variant="outline">
                <Upload className="mr-2 h-5 w-5" />
                Upload Job Description
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-6 w-6 text-blue-600" />
                Job Descriptions
              </CardTitle>
              <CardDescription>
                Upload and manage job descriptions with automatic skill extraction
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/upload-jd">
                <Button className="w-full">Upload JD</Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-6 w-6 text-green-600" />
                Candidates
              </CardTitle>
              <CardDescription>
                Upload resumes and automatically extract candidate skills and experience
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/upload-resume">
                <Button className="w-full">Upload Resume</Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-6 w-6 text-purple-600" />
                Analytics Dashboard
              </CardTitle>
              <CardDescription>
                View candidate rankings, bias alerts, and diversity metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/dashboard">
                <Button className="w-full">View Dashboard</Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <h2 className="text-3xl font-bold text-center mb-8">Key Features</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-semibold mb-4 text-blue-600">AI-Powered Matching</h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                <li>• Automatic skill extraction from resumes and job descriptions</li>
                <li>• TF-IDF and semantic similarity scoring</li>
                <li>• Comprehensive skill gap analysis</li>
                <li>• Experience and education matching</li>
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-4 text-green-600">Bias Detection</h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                <li>• Gender and experience bias alerts</li>
                <li>• Diversity metrics and scoring</li>
                <li>• Fair recruitment recommendations</li>
                <li>• Transparent explainability features</li>
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-4 text-purple-600">Interactive Insights</h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                <li>• Risk heatmaps by department</li>
                <li>• Real-time diversity tracking</li>
                <li>• Sentiment analysis widgets</li>
                <li>• Auto-refreshing dashboards</li>
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-4 text-orange-600">Workflow Automation</h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-300">
                <li>• One-click candidate shortlisting</li>
                <li>• Automated email notifications</li>
                <li>• Background task processing</li>
                <li>• Seamless HR integration</li>
              </ul>
            </div>
          </div>
        </div> */}
      </div>
    </div>
  );
}
