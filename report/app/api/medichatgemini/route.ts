import { queryPineconeVectorStore } from "@/utils";
import { Pinecone } from "@pinecone-database/pinecone";
// import { Message, OpenAIStream, StreamData, StreamingTextResponse } from "ai";
import { createGoogleGenerativeAI } from "@ai-sdk/google";
import { generateText, Message, StreamData, streamText } from "ai";

// Allow streaming responses up to 30 seconds
export const maxDuration = 60;
// export const runtime = 'edge';

const pinecone = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY ?? "",
});

const google = createGoogleGenerativeAI({
  baseURL: "https://generativelanguage.googleapis.com/v1beta",
  apiKey: process.env.GEMINI_API_KEY,
});

// gemini-1.5-pro-latest
// gemini-1.5-pro-exp-0801
const model = google("models/gemini-1.5-pro-latest", {
  safetySettings: [
    { category: "HARM_CATEGORY_DANGEROUS_CONTENT", threshold: "BLOCK_NONE" },
  ],
});

export async function POST(req: Request, res: Response) {
  const reqBody = await req.json();
  console.log(reqBody);

  const messages: Message[] = reqBody.messages;
  const userQuestion = `${messages[messages.length - 1].content}`;

  const reportData: string = reqBody.data.reportData;
  const query = `Represent this for searching relevant passages: patient medical report says: \n${reportData}. \n\n${userQuestion}`;

  const retrievals = await queryPineconeVectorStore(
    pinecone,
    "medical-books",
    "ns1",
    query
  );

  const finalPrompt = `As a medical expert, analyze this patient's clinical report and user query. Integrate ONLY RELEVANT information from the provided clinical findings. Structure your response with:

**1. Key Findings** (2-3 bullet points of critical report insights)
**2. Recommendations** (Actionable steps if applicable)

Formatting rules:
- Use clear headings with **bold**
- 1-2 sentence bullets
- Omit obvious/normal findings
- Flag critical values with ❗
- Never include irrelevant clinical findings

Patient Report: ${reportData}

User Query: ${userQuestion}

Clinical Findings: ${retrievals}

Response:`;

  const data = new StreamData();
  data.append({
    retrievals: retrievals,
  });

  const result = await streamText({
    model: model,
    prompt: finalPrompt,
    onFinish() {
      data.close();
    },
  });

  return result.toDataStreamResponse({ data });
}
