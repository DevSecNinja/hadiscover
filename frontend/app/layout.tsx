import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "hadiscover - Discover Home Assistant Automations",
  description:
    "Search and explore powerful Home Assistant automations from the community. Find triggers, actions, and blueprints shared on GitHub.",
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any", type: "image/x-icon" },
      { url: "/icon.png", sizes: "48x48", type: "image/png" },
    ],
    apple: [
      { url: "/apple-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
