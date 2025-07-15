-- InterviewAgent Complete Database Setup (Fixed)
-- Run this script in Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE application_status AS ENUM ('pending', 'submitted', 'failed', 'confirmed');
CREATE TYPE job_status AS ENUM ('discovered', 'filtered', 'applied', 'rejected');
CREATE TYPE agent_status AS ENUM ('started', 'completed', 'failed');

-- Users table (simplified for single-user MVP)
CREATE TABLE IF NOT EXISTS public.users (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Resume templates table
CREATE TABLE IF NOT EXISTS public.resume_templates (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  content TEXT NOT NULL,
  file_url TEXT,
  is_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Job sites configuration table
CREATE TABLE IF NOT EXISTS public.job_sites (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  url TEXT NOT NULL,
  is_enabled BOOLEAN DEFAULT TRUE,
  credentials_encrypted TEXT,
  last_scraped TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Job listings table
CREATE TABLE IF NOT EXISTS public.job_listings (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  job_site_id UUID REFERENCES public.job_sites(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  company TEXT NOT NULL,
  location TEXT,
  description TEXT NOT NULL DEFAULT '',
  requirements TEXT,
  salary_range TEXT,
  job_url TEXT NOT NULL,
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  applied_at TIMESTAMP WITH TIME ZONE,
  status job_status DEFAULT 'discovered',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW') NOT NULL,
  UNIQUE(job_url)
);

-- Applications table
CREATE TABLE IF NOT EXISTS public.applications (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  job_listing_id UUID REFERENCES public.job_listings(id) ON DELETE CASCADE NOT NULL,
  resume_template_id UUID REFERENCES public.resume_templates(id) NOT NULL,
  cover_letter_content TEXT,
  status application_status DEFAULT 'pending',
  application_data JSONB,
  submitted_at TIMESTAMP WITH TIME ZONE,
  confirmation_data JSONB,
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Schedules table for automation (simplified for MVP)
CREATE TABLE IF NOT EXISTS public.schedules (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  cron_expression TEXT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  job_sites TEXT[] NOT NULL DEFAULT '{}',
  filters JSONB DEFAULT '{}',
  last_run TIMESTAMP WITH TIME ZONE,
  next_run TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Agent logs table for tracking agent activities
CREATE TABLE IF NOT EXISTS public.agent_logs (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
  agent_type TEXT NOT NULL,
  action TEXT NOT NULL,
  status agent_status DEFAULT 'started',
  data JSONB,
  error_message TEXT,
  duration_ms INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Agent results table for storing agent execution results
CREATE TABLE IF NOT EXISTS public.agent_results (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  agent_type TEXT NOT NULL,
  task_type TEXT NOT NULL,
  input_data JSONB NOT NULL,
  output_data JSONB NOT NULL,
  success BOOLEAN NOT NULL,
  error_message TEXT,
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Cover letters table for storing generated cover letters
CREATE TABLE IF NOT EXISTS public.cover_letters (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  job_title TEXT NOT NULL,
  company_name TEXT NOT NULL,
  cover_letter_content TEXT NOT NULL,
  quality_score INTEGER,
  generation_type TEXT DEFAULT 'standard',
  agent_result_id UUID REFERENCES public.agent_results(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Optimized resumes table for storing resume optimizations
CREATE TABLE IF NOT EXISTS public.optimized_resumes (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  original_resume_id UUID REFERENCES public.resume_templates(id) ON DELETE CASCADE NOT NULL,
  job_title TEXT NOT NULL,
  company_name TEXT NOT NULL,
  optimized_content TEXT NOT NULL,
  job_match_score INTEGER,
  optimization_type TEXT DEFAULT 'standard',
  agent_result_id UUID REFERENCES public.agent_results(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Job searches table for storing job search results
CREATE TABLE IF NOT EXISTS public.job_searches (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  search_query TEXT NOT NULL,
  search_criteria JSONB NOT NULL,
  jobs_found INTEGER NOT NULL,
  search_results JSONB NOT NULL,
  agent_result_id UUID REFERENCES public.agent_results(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_resume_templates_user_id ON public.resume_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_job_sites_user_id ON public.job_sites(user_id);
CREATE INDEX IF NOT EXISTS idx_job_listings_job_site_id ON public.job_listings(job_site_id);
CREATE INDEX IF NOT EXISTS idx_job_listings_status ON public.job_listings(status);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON public.applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_listing_id ON public.applications(job_listing_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON public.applications(status);
CREATE INDEX IF NOT EXISTS idx_schedules_user_id ON public.schedules(user_id);
CREATE INDEX IF NOT EXISTS idx_schedules_is_active ON public.schedules(is_active);
CREATE INDEX IF NOT EXISTS idx_agent_logs_user_id ON public.agent_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent_type ON public.agent_logs(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_logs_created_at ON public.agent_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_results_user_id ON public.agent_results(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_results_agent_type ON public.agent_results(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_results_task_type ON public.agent_results(task_type);
CREATE INDEX IF NOT EXISTS idx_agent_results_created_at ON public.agent_results(created_at);
CREATE INDEX IF NOT EXISTS idx_cover_letters_user_id ON public.cover_letters(user_id);
CREATE INDEX IF NOT EXISTS idx_cover_letters_company_name ON public.cover_letters(company_name);
CREATE INDEX IF NOT EXISTS idx_cover_letters_created_at ON public.cover_letters(created_at);
CREATE INDEX IF NOT EXISTS idx_optimized_resumes_user_id ON public.optimized_resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_optimized_resumes_original_resume_id ON public.optimized_resumes(original_resume_id);
CREATE INDEX IF NOT EXISTS idx_optimized_resumes_created_at ON public.optimized_resumes(created_at);
CREATE INDEX IF NOT EXISTS idx_job_searches_user_id ON public.job_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_job_searches_created_at ON public.job_searches(created_at);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = TIMEZONE('utc'::text, NOW());
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing triggers if they exist (to avoid conflicts)
DROP TRIGGER IF EXISTS set_users_updated_at ON public.users;
DROP TRIGGER IF EXISTS set_resume_templates_updated_at ON public.resume_templates;
DROP TRIGGER IF EXISTS set_job_sites_updated_at ON public.job_sites;
DROP TRIGGER IF EXISTS set_job_listings_updated_at ON public.job_listings;
DROP TRIGGER IF EXISTS set_applications_updated_at ON public.applications;
DROP TRIGGER IF EXISTS set_schedules_updated_at ON public.schedules;
DROP TRIGGER IF EXISTS set_agent_results_updated_at ON public.agent_results;
DROP TRIGGER IF EXISTS set_cover_letters_updated_at ON public.cover_letters;
DROP TRIGGER IF EXISTS set_optimized_resumes_updated_at ON public.optimized_resumes;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER set_users_updated_at
  BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER set_resume_templates_updated_at
  BEFORE UPDATE ON public.resume_templates
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER set_job_sites_updated_at
  BEFORE UPDATE ON public.job_sites
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER set_job_listings_updated_at
  BEFORE UPDATE ON public.job_listings
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER set_applications_updated_at
  BEFORE UPDATE ON public.applications
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER set_schedules_updated_at
  BEFORE UPDATE ON public.schedules
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER set_agent_results_updated_at
  BEFORE UPDATE ON public.agent_results
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER set_cover_letters_updated_at
  BEFORE UPDATE ON public.cover_letters
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER set_optimized_resumes_updated_at
  BEFORE UPDATE ON public.optimized_resumes
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

-- Verify tables were created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'resume_templates', 'job_sites', 'job_listings', 'applications', 'schedules', 'agent_logs', 'agent_results', 'cover_letters', 'optimized_resumes', 'job_searches')
ORDER BY table_name;