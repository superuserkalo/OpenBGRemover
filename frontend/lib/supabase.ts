import { createClient } from "@supabase/supabase-js"

const supabaseUrl = "https://bxwzgybcivctgasyhwur.supabase.co"
const supabaseAnonKey =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ4d3pneWJjaXZjdGdhc3lod3VyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAwNjM4NzcsImV4cCI6MjA2NTYzOTg3N30.Afvtx2mGin_9ug8AZEAf5904m6bGcHxsBiJV69Ib3gU"

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Server-side client for auth (if needed)
export const createServerClient = () => {
  return createClient(supabaseUrl, process.env.SUPABASE_SERVICE_ROLE_KEY!)
}
