import Script from "next/script";

/**
 * Umami analytics loader.
 *
 * Renders nothing until both env vars are set, so it's safe to ship dormant:
 *   NEXT_PUBLIC_UMAMI_SRC         e.g. https://<your-umami>.vercel.app/script.js
 *   NEXT_PUBLIC_UMAMI_WEBSITE_ID  the website id from Umami → Settings → Websites
 */
export function Umami() {
  const src = process.env.NEXT_PUBLIC_UMAMI_SRC;
  const websiteId = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID;

  if (!src || !websiteId) return null;

  return (
    <Script
      src={src}
      data-website-id={websiteId}
      strategy="afterInteractive"
    />
  );
}
