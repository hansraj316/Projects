-- Agent-related tables for InterviewAgent
-- Additional migrations for agent results and outputs

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

-- Triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS set_agent_results_updated_at
  BEFORE UPDATE ON public.agent_results
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER IF NOT EXISTS set_cover_letters_updated_at
  BEFORE UPDATE ON public.cover_letters
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER IF NOT EXISTS set_optimized_resumes_updated_at
  BEFORE UPDATE ON public.optimized_resumes
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();