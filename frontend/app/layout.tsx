import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Content Filter",
  description: "Create rules and highlight matching text.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
