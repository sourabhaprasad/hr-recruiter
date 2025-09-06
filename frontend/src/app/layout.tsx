import Link from "next/link";
import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900">
        <nav className="p-4 bg-gray-100 flex gap-4">
          <Link href="/upload-jd">Upload JD</Link>
          <Link href="/upload-resume">Upload Resume</Link>
          <Link href="/dashboard">Dashboard</Link>
        </nav>
        {children}
      </body>
    </html>
  );
}
