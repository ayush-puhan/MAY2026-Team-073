import React from 'react';
import { Header } from '../../assets/components/landing/Header/Header';
import { HeroSection } from '../../assets/components/landing/HeroSection/HeroSection';
import { CampusPulse } from '../../assets/components/landing/CampusPulse/CampusPulse';
import { FeaturedClubs } from '../../assets/components/landing/FeaturedClubs/FeaturedClubs';
import { StatsSection } from '../../assets/components/landing/StatsSection/StatsSection';
import { Testimonials } from '../../assets/components/landing/Testimonials/Testimonials';
import { CTASection } from '../../assets/components/landing/CTASection/CTASection';
import { Footer } from '../../assets/components/landing/Footer/Footer';

/**
 * Landing Page — 8 Section Components:
 * 1. Navbar (Header)
 * 2. HeroSection
 * 3. CampusPulse
 * 4. FeaturedClubs
 * 5. StatsSection
 * 6. Testimonials
 * 7. CTASection
 * 8. Footer
 */
export const Landing = () => {
  return (
    <>
      <Header />
      <HeroSection />
      <CampusPulse />
      <FeaturedClubs />
      <StatsSection />
      <Testimonials />
      <CTASection />
      <Footer />
    </>
  );
};
