export interface MessageModel {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  query: string;
  conversation_id?: string;
  history: MessageModel[];
}

export interface SubQueryModel {
  text: string;
  category: string;
  confidence: number;
}

export interface CitationModel {
  sourceFile: string;
  category: string;
  chunkPreview: string;
  score: number;
  scoreType: string;
  chunkId: string;
}

export interface AnalyticsModel {
  categories: string[];
  complexity: string;
  confidence: number;
  strategy: string;
  latencyMs: number;
  subQueries: SubQueryModel[];
  chunksRetrieved: number;
  chunksSentToLLM: number;
  isFreshness: boolean;
  isMultiQuery: boolean;
  fallbackTriggered: boolean;
  domainDetected: boolean;
  outOfDomain: boolean;
}

export interface ChatResponse {
  content: string;
  analytics: AnalyticsModel;
  citations: CitationModel[];
}

export interface HealthResponse {
  status: string;
  vector_db: string;
  bm25: string;
  documents: number;
  chunks: number;
  llm: string;
}
