                                   

--- DOCUMENT: https://docs.ollama.com/ ---
# Ollama's documentation
Copy page
Copy page
![](https://mintcdn.com/ollama-9269c548/w-L7kuDqk3_8zi5c/images/welcome.png?fit=max&auto=format&n=w-L7kuDqk3_8zi5c&q=85&s=914368bbe8709d04481a8a478b66cf8c) [Ollama](https://ollama.com) is the easiest way to get up and running with large language models such as gpt-oss, Gemma 3, DeepSeek-R1, Qwen3 and more.
## Quickstart
Get up and running with your first model or integrate Ollama with your favorite tools
## Download Ollama
Download Ollama on macOS, Windows or Linux
## Cloud
Ollama’s cloud models offer larger models with better performance.
## API reference
View Ollama’s API reference
##
[​](https://docs.ollama.com/#libraries)
Libraries
## Ollama's Python Library
The official library for using Ollama with Python
## Ollama's JavaScript library
The official library for using Ollama with JavaScript or TypeScript.
## Community libraries
View a list of 20+ community-supported libraries for Ollama
##
[​](https://docs.ollama.com/#community)
Community
## Discord
Join our Discord community
## Reddit
Join our Reddit community
[ Quickstart Next ](https://docs.ollama.com/quickstart)
⌘I
On this page
  * [Libraries](https://docs.ollama.com/#libraries)
  * [Community](https://docs.ollama.com/#community)


--- DOCUMENT: https://docs.ollama.com/api/introduction ---
# Introduction
Copy page
Copy page
Ollama’s API allows you to run and interact with models programatically.
##
[​](https://docs.ollama.com/api/introduction#get-started)
Get started
If you’re just getting started, follow the [quickstart](https://docs.ollama.com/quickstart) documentation to get up and running with Ollama’s API.
##
[​](https://docs.ollama.com/api/introduction#base-url)
Base URL
After installation, Ollama’s API is served by default at:

```
http://localhost:11434/api

```

For running cloud models on **ollama.com** , the same API is available with the following base URL:

```
https://ollama.com/api

```

##
[​](https://docs.ollama.com/api/introduction#example-request)
Example request
Once Ollama is running, its API is automatically available and can be accessed via `curl`:

```
curl http://localhost:11434/api/generate -d '{
  "model": "gemma3",
  "prompt": "Why is the sky blue?"
}'

```

##
[​](https://docs.ollama.com/api/introduction#libraries)
Libraries
Ollama has official libraries for Python and JavaScript:
  * [Python](https://github.com/ollama/ollama-python)
  * [JavaScript](https://github.com/ollama/ollama-js)

Several community-maintained libraries are available for Ollama. For a full list, see the [Ollama GitHub repository](https://github.com/ollama/ollama?tab=readme-ov-file#libraries-1).
##
[​](https://docs.ollama.com/api/introduction#versioning)
Versioning
Ollama’s API isn’t strictly versioned, but the API is expected to be stable and backwards compatible. Deprecations are rare and will be announced in the [release notes](https://github.com/ollama/ollama/releases).
[ Authentication Next ](https://docs.ollama.com/api/authentication)
⌘I
On this page
  * [Get started](https://docs.ollama.com/api/introduction#get-started)
  * [Base URL](https://docs.ollama.com/api/introduction#base-url)
  * [Example request](https://docs.ollama.com/api/introduction#example-request)
  * [Libraries](https://docs.ollama.com/api/introduction#libraries)
  * [Versioning](https://docs.ollama.com/api/introduction#versioning)


--- DOCUMENT: https://docs.ollama.com/capabilities/embeddings ---
# Embeddings
Copy page
Generate text embeddings for semantic search, retrieval, and RAG.
Copy page
Embeddings turn text into numeric vectors you can store in a vector database, search with cosine similarity, or use in RAG pipelines. The vector length depends on the model (typically 384–1024 dimensions).
##
[​](https://docs.ollama.com/capabilities/embeddings#recommended-models)
Recommended models
  * [embeddinggemma](https://ollama.com/library/embeddinggemma)
  * [qwen3-embedding](https://ollama.com/library/qwen3-embedding)
  * [all-minilm](https://ollama.com/library/all-minilm)


##
[​](https://docs.ollama.com/capabilities/embeddings#generate-embeddings)
Generate embeddings
  * CLI
  * cURL
  * Python
  * JavaScript


Generate embeddings directly from the command line:

```
ollama run embeddinggemma "Hello world"

```

You can also pipe text to generate embeddings:

```
echo "Hello world" | ollama run embeddinggemma

```

Output is a JSON array.

```
curl -X POST http://localhost:11434/api/embed \
  -H "Content-Type: application/json" \
  -d '{
    "model": "embeddinggemma",
    "input": "The quick brown fox jumps over the lazy dog."
  }'

```


```
import ollama

single = ollama.embed(
  model='embeddinggemma',
  input='The quick brown fox jumps over the lazy dog.'
)
print(len(single['embeddings'][0]))  # vector length

```


```
import ollama from 'ollama'

const single = await ollama.embed({
  model: 'embeddinggemma',
  input: 'The quick brown fox jumps over the lazy dog.',
})
console.log(single.embeddings[0].length) // vector length

```

The `/api/embed` endpoint returns L2‑normalized (unit‑length) vectors.
##
[​](https://docs.ollama.com/capabilities/embeddings#generate-a-batch-of-embeddings)
Generate a batch of embeddings
Pass an array of strings to `input`.
  * cURL
  * Python
  * JavaScript


```
curl -X POST http://localhost:11434/api/embed \
  -H "Content-Type: application/json" \
  -d '{
    "model": "embeddinggemma",
    "input": [
      "First sentence",
      "Second sentence",
      "Third sentence"
    ]
  }'

```


```
import ollama

batch = ollama.embed(
  model='embeddinggemma',
  input=[
    'The quick brown fox jumps over the lazy dog.',
    'The five boxing wizards jump quickly.',
    'Jackdaws love my big sphinx of quartz.',
  ]
)
print(len(batch['embeddings']))  # number of vectors

```


```
import ollama from 'ollama'

const batch = await ollama.embed({
  model: 'embeddinggemma',
  input: [
    'The quick brown fox jumps over the lazy dog.',
    'The five boxing wizards jump quickly.',
    'Jackdaws love my big sphinx of quartz.',
  ],
})
console.log(batch.embeddings.length) // number of vectors

```

##
[​](https://docs.ollama.com/capabilities/embeddings#tips)
Tips
  * Use cosine similarity for most semantic search use cases.
  * Use the same embedding model for both indexing and querying.


[Previous](https://docs.ollama.com/capabilities/vision)[ Tool calling Next ](https://docs.ollama.com/capabilities/tool-calling)
⌘I
On this page
  * [Recommended models](https://docs.ollama.com/capabilities/embeddings#recommended-models)
  * [Generate embeddings](https://docs.ollama.com/capabilities/embeddings#generate-embeddings)
  * [Generate a batch of embeddings](https://docs.ollama.com/capabilities/embeddings#generate-a-batch-of-embeddings)
  * [Tips](https://docs.ollama.com/capabilities/embeddings#tips)


--- DOCUMENT: https://docs.ollama.com/capabilities/streaming ---
# Streaming
Copy page
Copy page
Streaming allows you to render text as it is produced by the model. Streaming is enabled by default through the REST API, but disabled by default in the SDKs. To enable streaming in the SDKs, set the `stream` parameter to `True`.
##
[​](https://docs.ollama.com/capabilities/streaming#key-streaming-concepts)
Key streaming concepts
  1. Chatting: Stream partial assistant messages. Each chunk includes the `content` so you can render messages as they arrive.
  2. Thinking: Thinking-capable models emit a `thinking` field alongside regular content in each chunk. Detect this field in streaming chunks to show or hide reasoning traces before the final answer arrives.
  3. Tool calling: Watch for streamed `tool_calls` in each chunk, execute the requested tool, and append tool outputs back into the conversation.


##
[​](https://docs.ollama.com/capabilities/streaming#handling-streamed-chunks)
Handling streamed chunks
It is necessary to accumulate the partial fields in order to maintain the history of the conversation. This is particularly important for tool calling where the thinking, tool call from the model, and the executed tool result must be passed back to the model in the next request.
  * Python
  * JavaScript


```
from ollama import chat

stream = chat(
  model='qwen3',
  messages=[{'role': 'user', 'content': 'What is 17 × 23?'}],
  stream=True,
)

in_thinking = False
content = ''
thinking = ''
for chunk in stream:
  if chunk.message.thinking:
    if not in_thinking:
      in_thinking = True
      print('Thinking:\n', end='', flush=True)
    print(chunk.message.thinking, end='', flush=True)
    # accumulate the partial thinking
    thinking += chunk.message.thinking
  elif chunk.message.content:
    if in_thinking:
      in_thinking = False
      print('\n\nAnswer:\n', end='', flush=True)
    print(chunk.message.content, end='', flush=True)
    # accumulate the partial content
    content += chunk.message.content

  # append the accumulated fields to the messages for the next request
  new_messages = [{ role: 'assistant', thinking: thinking, content: content }]

```


```
import ollama from 'ollama'

async function main() {
  const stream = await ollama.chat({
    model: 'qwen3',
    messages: [{ role: 'user', content: 'What is 17 × 23?' }],
    stream: true,
  })

  let inThinking = false
  let content = ''
  let thinking = ''

  for await (const chunk of stream) {
    if (chunk.message.thinking) {
      if (!inThinking) {
        inThinking = true
        process.stdout.write('Thinking:\n')
      }
      process.stdout.write(chunk.message.thinking)
      // accumulate the partial thinking
      thinking += chunk.message.thinking
    } else if (chunk.message.content) {
      if (inThinking) {
        inThinking = false
        process.stdout.write('\n\nAnswer:\n')
      }
      process.stdout.write(chunk.message.content)
      // accumulate the partial content
      content += chunk.message.content
    }
  }

  // append the accumulated fields to the messages for the next request
  new_messages = [{ role: 'assistant', thinking: thinking, content: content }]
}

main().catch(console.error)

```

[Previous](https://docs.ollama.com/cloud)[ Thinking Next ](https://docs.ollama.com/capabilities/thinking)
⌘I
On this page
  * [Key streaming concepts](https://docs.ollama.com/capabilities/streaming#key-streaming-concepts)
  * [Handling streamed chunks](https://docs.ollama.com/capabilities/streaming#handling-streamed-chunks)


--- DOCUMENT: https://docs.ollama.com/capabilities/structured-outputs ---
# Structured Outputs
Copy page
Copy page
Ollama’s Cloud currently does not support structured outputs.
Structured outputs let you enforce a JSON schema on model responses so you can reliably extract structured data, describe images, or keep every reply consistent.
##
[​](https://docs.ollama.com/capabilities/structured-outputs#generating-structured-json)
Generating structured JSON
  * cURL
  * Python
  * JavaScript


```
curl -X POST http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "gpt-oss",
  "messages": [{"role": "user", "content": "Tell me about Canada in one line"}],
  "stream": false,
  "format": "json"
}'

```


```
from ollama import chat

response = chat(
  model='gpt-oss',
  messages=[{'role': 'user', 'content': 'Tell me about Canada.'}],
  format='json'
)
print(response.message.content)

```


```
import ollama from 'ollama'

const response = await ollama.chat({
  model: 'gpt-oss',
  messages: [{ role: 'user', content: 'Tell me about Canada.' }],
  format: 'json'
})
console.log(response.message.content)

```

##
[​](https://docs.ollama.com/capabilities/structured-outputs#generating-structured-json-with-a-schema)
Generating structured JSON with a schema
Provide a JSON schema to the `format` field.
It is ideal to also pass the JSON schema as a string in the prompt to ground the model’s response.
  * cURL
  * Python
  * JavaScript


```
curl -X POST http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "gpt-oss",
  "messages": [{"role": "user", "content": "Tell me about Canada."}],
  "stream": false,
  "format": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "capital": {"type": "string"},
      "languages": {
        "type": "array",
        "items": {"type": "string"}
      }
    },
    "required": ["name", "capital", "languages"]
  }
}'

```

Use Pydantic models and pass `model_json_schema()` to `format`, then validate the response:

```
from ollama import chat
from pydantic import BaseModel

class Country(BaseModel):
  name: str
  capital: str
  languages: list[str]

response = chat(
  model='gpt-oss',
  messages=[{'role': 'user', 'content': 'Tell me about Canada.'}],
  format=Country.model_json_schema(),
)

country = Country.model_validate_json(response.message.content)
print(country)

```

Serialize a Zod schema with `zodToJsonSchema()` and parse the structured response:

```
import ollama from 'ollama'
import { z } from 'zod'
import { zodToJsonSchema } from 'zod-to-json-schema'

const Country = z.object({
  name: z.string(),
  capital: z.string(),
  languages: z.array(z.string()),
})

const response = await ollama.chat({
  model: 'gpt-oss',
  messages: [{ role: 'user', content: 'Tell me about Canada.' }],
  format: zodToJsonSchema(Country),
})

const country = Country.parse(JSON.parse(response.message.content))
console.log(country)

```

##
[​](https://docs.ollama.com/capabilities/structured-outputs#example-extract-structured-data)
Example: Extract structured data
Define the objects you want returned and let the model populate the fields:

```
from ollama import chat
from pydantic import BaseModel

class Pet(BaseModel):
  name: str
  animal: str
  age: int
  color: str | None
  favorite_toy: str | None

class PetList(BaseModel):
  pets: list[Pet]

response = chat(
  model='gpt-oss',
  messages=[{'role': 'user', 'content': 'I have two cats named Luna and Loki...'}],
  format=PetList.model_json_schema(),
)

pets = PetList.model_validate_json(response.message.content)
print(pets)

```

##
[​](https://docs.ollama.com/capabilities/structured-outputs#example-vision-with-structured-outputs)
Example: Vision with structured outputs
Vision models accept the same `format` parameter, enabling deterministic descriptions of images:

```
from ollama import chat
from pydantic import BaseModel
from typing import Literal, Optional

class Object(BaseModel):
  name: str
  confidence: float
  attributes: str

class ImageDescription(BaseModel):
  summary: str
  objects: list[Object]
  scene: str
  colors: list[str]
  time_of_day: Literal['Morning', 'Afternoon', 'Evening', 'Night']
  setting: Literal['Indoor', 'Outdoor', 'Unknown']
  text_content: Optional[str] = None

response = chat(
  model='gemma3',
  messages=[{
    'role': 'user',
    'content': 'Describe this photo and list the objects you detect.',
    'images': ['path/to/image.jpg'],
  }],
  format=ImageDescription.model_json_schema(),
  options={'temperature': 0},
)

image_description = ImageDescription.model_validate_json(response.message.content)
print(image_description)

```

##
[​](https://docs.ollama.com/capabilities/structured-outputs#tips-for-reliable-structured-outputs)
Tips for reliable structured outputs
  * Define schemas with Pydantic (Python) or Zod (JavaScript) so they can be reused for validation.
  * Lower the temperature (e.g., set it to `0`) for more deterministic completions.
  * Structured outputs work through the OpenAI-compatible API via `response_format`


[Previous](https://docs.ollama.com/capabilities/thinking)[ Vision Next ](https://docs.ollama.com/capabilities/vision)
⌘I
On this page
  * [Generating structured JSON](https://docs.ollama.com/capabilities/structured-outputs#generating-structured-json)
  * [Generating structured JSON with a schema](https://docs.ollama.com/capabilities/structured-outputs#generating-structured-json-with-a-schema)
  * [Example: Extract structured data](https://docs.ollama.com/capabilities/structured-outputs#example-extract-structured-data)
  * [Example: Vision with structured outputs](https://docs.ollama.com/capabilities/structured-outputs#example-vision-with-structured-outputs)
  * [Tips for reliable structured outputs](https://docs.ollama.com/capabilities/structured-outputs#tips-for-reliable-structured-outputs)


--- DOCUMENT: https://docs.ollama.com/capabilities/thinking ---
# Thinking
Copy page
Copy page
Thinking-capable models emit a `thinking` field that separates their reasoning trace from the final answer. Use this capability to audit model steps, animate the model _thinking_ in a UI, or hide the trace entirely when you only need the final response.
##
[​](https://docs.ollama.com/capabilities/thinking#supported-models)
Supported models
  * [Qwen 3](https://ollama.com/library/qwen3)
  * [GPT-OSS](https://ollama.com/library/gpt-oss) _(use`think` levels: `low`, `medium`, `high` — the trace cannot be fully disabled)_
  * [DeepSeek-v3.1](https://ollama.com/library/deepseek-v3.1)
  * [DeepSeek R1](https://ollama.com/library/deepseek-r1)
  * Browse the latest additions under [thinking models](https://ollama.com/search?c=thinking)


##
[​](https://docs.ollama.com/capabilities/thinking#enable-thinking-in-api-calls)
Enable thinking in API calls
Set the `think` field on chat or generate requests. Most models accept booleans (`true`/`false`). GPT-OSS instead expects one of `low`, `medium`, or `high` to tune the trace length. The `message.thinking` (chat endpoint) or `thinking` (generate endpoint) field contains the reasoning trace while `message.content` / `response` holds the final answer.
  * cURL
  * Python
  * JavaScript


```
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3",
  "messages": [{
    "role": "user",
    "content": "How many letter r are in strawberry?"
  }],
  "think": true,
  "stream": false
}'

```


```
from ollama import chat

response = chat(
  model='qwen3',
  messages=[{'role': 'user', 'content': 'How many letter r are in strawberry?'}],
  think=True,
  stream=False,
)

print('Thinking:\n', response.message.thinking)
print('Answer:\n', response.message.content)

```


```
import ollama from 'ollama'

const response = await ollama.chat({
  model: 'deepseek-r1',
  messages: [{ role: 'user', content: 'How many letter r are in strawberry?' }],
  think: true,
  stream: false,
})

console.log('Thinking:\n', response.message.thinking)
console.log('Answer:\n', response.message.content)

```

GPT-OSS requires `think` to be set to `"low"`, `"medium"`, or `"high"`. Passing `true`/`false` is ignored for that model.
##
[​](https://docs.ollama.com/capabilities/thinking#stream-the-reasoning-trace)
Stream the reasoning trace
Thinking streams interleave reasoning tokens before answer tokens. Detect the first `thinking` chunk to render a “thinking” section, then switch to the final reply once `message.content` arrives.
  * Python
  * JavaScript


```
from ollama import chat

stream = chat(
  model='qwen3',
  messages=[{'role': 'user', 'content': 'What is 17 × 23?'}],
  think=True,
  stream=True,
)

in_thinking = False

for chunk in stream:
  if chunk.message.thinking and not in_thinking:
    in_thinking = True
    print('Thinking:\n', end='')

  if chunk.message.thinking:
    print(chunk.message.thinking, end='')
  elif chunk.message.content:
    if in_thinking:
      print('\n\nAnswer:\n', end='')
      in_thinking = False
    print(chunk.message.content, end='')


```


```
import ollama from 'ollama'

async function main() {
  const stream = await ollama.chat({
    model: 'qwen3',
    messages: [{ role: 'user', content: 'What is 17 × 23?' }],
    think: true,
    stream: true,
  })

  let inThinking = false

  for await (const chunk of stream) {
    if (chunk.message.thinking && !inThinking) {
      inThinking = true
      process.stdout.write('Thinking:\n')
    }

    if (chunk.message.thinking) {
      process.stdout.write(chunk.message.thinking)
    } else if (chunk.message.content) {
      if (inThinking) {
        process.stdout.write('\n\nAnswer:\n')
        inThinking = false
      }
      process.stdout.write(chunk.message.content)
    }
  }
}

main()

```

##
[​](https://docs.ollama.com/capabilities/thinking#cli-quick-reference)
CLI quick reference
  * Enable thinking for a single run: `ollama run deepseek-r1 --think "Where should I visit in Lisbon?"`
  * Disable thinking: `ollama run deepseek-r1 --think=false "Summarize this article"`
  * Hide the trace while still using a thinking model: `ollama run deepseek-r1 --hidethinking "Is 9.9 bigger or 9.11?"`
  * Inside interactive sessions, toggle with `/set think` or `/set nothink`.
  * GPT-OSS only accepts levels: `ollama run gpt-oss --think=low "Draft a headline"` (replace `low` with `medium` or `high` as needed).


Thinking is enabled by default in the CLI and API for supported models.
[Previous](https://docs.ollama.com/capabilities/streaming)[ Structured Outputs Next ](https://docs.ollama.com/capabilities/structured-outputs)
⌘I
On this page
  * [Supported models](https://docs.ollama.com/capabilities/thinking#supported-models)
  * [Enable thinking in API calls](https://docs.ollama.com/capabilities/thinking#enable-thinking-in-api-calls)
  * [Stream the reasoning trace](https://docs.ollama.com/capabilities/thinking#stream-the-reasoning-trace)
  * [CLI quick reference](https://docs.ollama.com/capabilities/thinking#cli-quick-reference)


--- DOCUMENT: https://docs.ollama.com/capabilities/tool-calling ---
# Tool calling
Copy page
Copy page
Ollama supports tool calling (also known as function calling) which allows a model to invoke tools and incorporate their results into its replies.
##
[​](https://docs.ollama.com/capabilities/tool-calling#calling-a-single-tool)
Calling a single tool
Invoke a single tool and include its response in a follow-up request. Also known as “single-shot” tool calling.
  * cURL
  * Python
  * JavaScript


```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "qwen3",
  "messages": [{"role": "user", "content": "What is the temperature in New York?"}],
  "stream": false,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_temperature",
        "description": "Get the current temperature for a city",
        "parameters": {
          "type": "object",
          "required": ["city"],
          "properties": {
            "city": {"type": "string", "description": "The name of the city"}
          }
        }
      }
    }
  ]
}'

```

**Generate a response with a single tool result**

```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "qwen3",
  "messages": [
    {"role": "user", "content": "What is the temperature in New York?"},
    {
      "role": "assistant",
      "tool_calls": [
        {
          "type": "function",
          "function": {
            "index": 0,
            "name": "get_temperature",
            "arguments": {"city": "New York"}
          }
        }
      ]
    },
    {"role": "tool", "tool_name": "get_temperature", "content": "22°C"}
  ],
  "stream": false
}'

```

Install the Ollama Python SDK:

```
# with pip
pip install ollama -U

# with uv
uv add ollama

```


```
from ollama import chat

def get_temperature(city: str) -> str:
  """Get the current temperature for a city

  Args:
    city: The name of the city

  Returns:
    The current temperature for the city
  """
  temperatures = {
    "New York": "22°C",
    "London": "15°C",
    "Tokyo": "18°C",
  }
  return temperatures.get(city, "Unknown")

messages = [{"role": "user", "content": "What is the temperature in New York?"}]

# pass functions directly as tools in the tools list or as a JSON schema
response = chat(model="qwen3", messages=messages, tools=[get_temperature], think=True)

messages.append(response.message)
if response.message.tool_calls:
  # only recommended for models which only return a single tool call
  call = response.message.tool_calls[0]
  result = get_temperature(**call.function.arguments)
  # add the tool result to the messages
  messages.append({"role": "tool", "tool_name": call.function.name, "content": str(result)})

  final_response = chat(model="qwen3", messages=messages, tools=[get_temperature], think=True)
  print(final_response.message.content)

```

Install the Ollama JavaScript library:

```
# with npm
npm i ollama

# with bun
bun i ollama

```


```
import ollama from 'ollama'

function getTemperature(city: string): string {
  const temperatures: Record<string, string> = {
    'New York': '22°C',
    'London': '15°C',
    'Tokyo': '18°C',
  }
  return temperatures[city] ?? 'Unknown'
}

const tools = [
  {
    type: 'function',
    function: {
      name: 'get_temperature',
      description: 'Get the current temperature for a city',
      parameters: {
        type: 'object',
        required: ['city'],
        properties: {
          city: { type: 'string', description: 'The name of the city' },
        },
      },
    },
  },
]

const messages = [{ role: 'user', content: "What is the temperature in New York?" }]

const response = await ollama.chat({
  model: 'qwen3',
  messages,
  tools,
  think: true,
})

messages.push(response.message)
if (response.message.tool_calls?.length) {
  // only recommended for models which only return a single tool call
  const call = response.message.tool_calls[0]
  const args = call.function.arguments as { city: string }
  const result = getTemperature(args.city)
  // add the tool result to the messages
  messages.push({ role: 'tool', tool_name: call.function.name, content: result })

  // generate the final response
  const finalResponse = await ollama.chat({ model: 'qwen3', messages, tools, think: true })
  console.log(finalResponse.message.content)
}

```

##
[​](https://docs.ollama.com/capabilities/tool-calling#parallel-tool-calling)
Parallel tool calling
  * cURL
  * Python
  * JavaScript


Request multiple tool calls in parallel, then send all tool responses back to the model.

```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "qwen3",
  "messages": [{"role": "user", "content": "What are the current weather conditions and temperature in New York and London?"}],
  "stream": false,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_temperature",
        "description": "Get the current temperature for a city",
        "parameters": {
          "type": "object",
          "required": ["city"],
          "properties": {
            "city": {"type": "string", "description": "The name of the city"}
          }
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "get_conditions",
        "description": "Get the current weather conditions for a city",
        "parameters": {
          "type": "object",
          "required": ["city"],
          "properties": {
            "city": {"type": "string", "description": "The name of the city"}
          }
        }
      }
    }
  ]
}'

```

**Generate a response with multiple tool results**

```
curl -s http://localhost:11434/api/chat -H "Content-Type: application/json" -d '{
  "model": "qwen3",
  "messages": [
    {"role": "user", "content": "What are the current weather conditions and temperature in New York and London?"},
    {
      "role": "assistant",
      "tool_calls": [
        {
          "type": "function",
          "function": {
            "index": 0,
            "name": "get_temperature",
            "arguments": {"city": "New York"}
          }
        },
        {
          "type": "function",
          "function": {
            "index": 1,
            "name": "get_conditions",
            "arguments": {"city": "New York"}
          }
        },
        {
          "type": "function",
          "function": {
            "index": 2,
            "name": "get_temperature",
            "arguments": {"city": "London"}
          }
        },
        {
          "type": "function",
          "function": {
            "index": 3,
            "name": "get_conditions",
            "arguments": {"city": "London"}
          }
        }
      ]
    },
    {"role": "tool", "tool_name": "get_temperature", "content": "22°C"},
    {"role": "tool", "tool_name": "get_conditions", "content": "Partly cloudy"},
    {"role": "tool", "tool_name": "get_temperature", "content": "15°C"},
    {"role": "tool", "tool_name": "get_conditions", "content": "Rainy"}
  ],
  "stream": false
}'

```


```
from ollama import chat

def get_temperature(city: str) -> str:
  """Get the current temperature for a city

  Args:
    city: The name of the city

  Returns:
    The current temperature for the city
  """
  temperatures = {
    "New York": "22°C",
    "London": "15°C",
    "Tokyo": "18°C"
  }
  return temperatures.get(city, "Unknown")

def get_conditions(city: str) -> str:
  """Get the current weather conditions for a city

  Args:
    city: The name of the city

  Returns:
    The current weather conditions for the city
  """
  conditions = {
    "New York": "Partly cloudy",
    "London": "Rainy",
    "Tokyo": "Sunny"
  }
  return conditions.get(city, "Unknown")


messages = [{'role': 'user', 'content': 'What are the current weather conditions and temperature in New York and London?'}]

# The python client automatically parses functions as a tool schema so we can pass them directly
# Schemas can be passed directly in the tools list as well
response = chat(model='qwen3', messages=messages, tools=[get_temperature, get_conditions], think=True)

# add the assistant message to the messages
messages.append(response.message)
if response.message.tool_calls:
  # process each tool call
  for call in response.message.tool_calls:
    # execute the appropriate tool
    if call.function.name == 'get_temperature':
      result = get_temperature(**call.function.arguments)
    elif call.function.name == 'get_conditions':
      result = get_conditions(**call.function.arguments)
    else:
      result = 'Unknown tool'
    # add the tool result to the messages
    messages.append({'role': 'tool',  'tool_name': call.function.name, 'content': str(result)})

  # generate the final response
  final_response = chat(model='qwen3', messages=messages, tools=[get_temperature, get_conditions], think=True)
  print(final_response.message.content)

```


```
import ollama from 'ollama'

function getTemperature(city: string): string {
  const temperatures: { [key: string]: string } = {
    "New York": "22°C",
    "London": "15°C",
    "Tokyo": "18°C"
  }
  return temperatures[city] || "Unknown"
}

function getConditions(city: string): string {
  const conditions: { [key: string]: string } = {
    "New York": "Partly cloudy",
    "London": "Rainy",
    "Tokyo": "Sunny"
  }
  return conditions[city] || "Unknown"
}

const tools = [
  {
    type: 'function',
    function: {
      name: 'get_temperature',
      description: 'Get the current temperature for a city',
      parameters: {
        type: 'object',
        required: ['city'],
        properties: {
          city: { type: 'string', description: 'The name of the city' },
        },
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'get_conditions',
      description: 'Get the current weather conditions for a city',
      parameters: {
        type: 'object',
        required: ['city'],
        properties: {
          city: { type: 'string', description: 'The name of the city' },
        },
      },
    },
  }
]

const messages = [{ role: 'user', content: 'What are the current weather conditions and temperature in New York and London?' }]

const response = await ollama.chat({
  model: 'qwen3',
  messages,
  tools,
  think: true
})

// add the assistant message to the messages
messages.push(response.message)
if (response.message.tool_calls) {
  // process each tool call
  for (const call of response.message.tool_calls) {
    // execute the appropriate tool
    let result: string
    if (call.function.name === 'get_temperature') {
      const args = call.function.arguments as { city: string }
      result = getTemperature(args.city)
    } else if (call.function.name === 'get_conditions') {
      const args = call.function.arguments as { city: string }
      result = getConditions(args.city)
    } else {
      result = 'Unknown tool'
    }
    // add the tool result to the messages
    messages.push({ role: 'tool', tool_name: call.function.name, content: result })
  }

  // generate the final response
  const finalResponse = await ollama.chat({ model: 'qwen3', messages, tools, think: true })
  console.log(finalResponse.message.content)
}

```

##
[​](https://docs.ollama.com/capabilities/tool-calling#multi-turn-tool-calling-agent-loop)
Multi-turn tool calling (Agent loop)
An agent loop allows the model to decide when to invoke tools and incorporate their results into its replies. It also might help to tell the model that it is in a loop and can make multiple tool calls.
  * Python
  * JavaScript


```
from ollama import chat, ChatResponse


def add(a: int, b: int) -> int:
  """Add two numbers"""
  """
  Args:
    a: The first number
    b: The second number

  Returns:
    The sum of the two numbers
  """
  return a + b


def multiply(a: int, b: int) -> int:
  """Multiply two numbers"""
  """
  Args:
    a: The first number
    b: The second number

  Returns:
    The product of the two numbers
  """
  return a * b


available_functions = {
  'add': add,
  'multiply': multiply,
}

messages = [{'role': 'user', 'content': 'What is (11434+12341)*412?'}]
while True:
    response: ChatResponse = chat(
        model='qwen3',
        messages=messages,
        tools=[add, multiply],
        think=True,
    )
    messages.append(response.message)
    print("Thinking: ", response.message.thinking)
    print("Content: ", response.message.content)
    if response.message.tool_calls:
        for tc in response.message.tool_calls:
            if tc.function.name in available_functions:
                print(f"Calling {tc.function.name} with arguments {tc.function.arguments}")
                result = available_functions[tc.function.name](**tc.function.arguments)
                print(f"Result: {result}")
                # add the tool result to the messages
                messages.append({'role': 'tool', 'tool_name': tc.function.name, 'content': str(result)})
    else:
        # end the loop when there are no more tool calls
        break
  # continue the loop with the updated messages

```


```
import ollama from 'ollama'

type ToolName = 'add' | 'multiply'

function add(a: number, b: number): number {
  return a + b
}

function multiply(a: number, b: number): number {
  return a * b
}

const availableFunctions: Record<ToolName, (a: number, b: number) => number> = {
  add,
  multiply,
}

const tools = [
  {
    type: 'function',
    function: {
      name: 'add',
      description: 'Add two numbers',
      parameters: {
        type: 'object',
        required: ['a', 'b'],
        properties: {
          a: { type: 'integer', description: 'The first number' },
          b: { type: 'integer', description: 'The second number' },
        },
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'multiply',
      description: 'Multiply two numbers',
      parameters: {
        type: 'object',
        required: ['a', 'b'],
        properties: {
          a: { type: 'integer', description: 'The first number' },
          b: { type: 'integer', description: 'The second number' },
        },
      },
    },
  },
]

async function agentLoop() {
  const messages = [{ role: 'user', content: 'What is (11434+12341)*412?' }]

  while (true) {
    const response = await ollama.chat({
      model: 'qwen3',
      messages,
      tools,
      think: true,
    })

    messages.push(response.message)
    console.log('Thinking:', response.message.thinking)
    console.log('Content:', response.message.content)

    const toolCalls = response.message.tool_calls ?? []
    if (toolCalls.length) {
      for (const call of toolCalls) {
        const fn = availableFunctions[call.function.name as ToolName]
        if (!fn) {
          continue
        }

        const args = call.function.arguments as { a: number; b: number }
        console.log(`Calling ${call.function.name} with arguments`, args)
        const result = fn(args.a, args.b)
        console.log(`Result: ${result}`)
        messages.push({ role: 'tool', tool_name: call.function.name, content: String(result) })
      }
    } else {
      break
    }
  }
}

agentLoop().catch(console.error)

```

##
[​](https://docs.ollama.com/capabilities/tool-calling#tool-calling-with-streaming)
Tool calling with streaming
When streaming, gather every chunk of `thinking`, `content`, and `tool_calls`, then return those fields together with any tool results in the follow-up request.
  * Python
  * JavaScript


```
from ollama import chat


def get_temperature(city: str) -> str:
  """Get the current temperature for a city

  Args:
    city: The name of the city

  Returns:
    The current temperature for the city
  """
  temperatures = {
    'New York': '22°C',
    'London': '15°C',
  }
  return temperatures.get(city, 'Unknown')


messages = [{'role': 'user', 'content': "What is the temperature in New York?"}]

while True:
  stream = chat(
    model='qwen3',
    messages=messages,
    tools=[get_temperature],
    stream=True,
    think=True,
  )

  thinking = ''
  content = ''
  tool_calls = []

  done_thinking = False
  # accumulate the partial fields
  for chunk in stream:
    if chunk.message.thinking:
      thinking += chunk.message.thinking
      print(chunk.message.thinking, end='', flush=True)
    if chunk.message.content:
      if not done_thinking:
        done_thinking = True
        print('\n')
      content += chunk.message.content
      print(chunk.message.content, end='', flush=True)
    if chunk.message.tool_calls:
      tool_calls.extend(chunk.message.tool_calls)
      print(chunk.message.tool_calls)

  # append accumulated fields to the messages
  if thinking or content or tool_calls:
    messages.append({'role': 'assistant', 'thinking': thinking, 'content': content, 'tool_calls': tool_calls})

  if not tool_calls:
    break

  for call in tool_calls:
    if call.function.name == 'get_temperature':
      result = get_temperature(**call.function.arguments)
    else:
      result = 'Unknown tool'
    messages.append({'role': 'tool', 'tool_name': call.function.name, 'content': result})

```


```
import ollama from 'ollama'

function getTemperature(city: string): string {
  const temperatures: Record<string, string> = {
    'New York': '22°C',
    'London': '15°C',
  }
  return temperatures[city] ?? 'Unknown'
}

const getTemperatureTool = {
  type: 'function',
  function: {
    name: 'get_temperature',
    description: 'Get the current temperature for a city',
    parameters: {
      type: 'object',
      required: ['city'],
      properties: {
        city: { type: 'string', description: 'The name of the city' },
      },
    },
  },
}

async function agentLoop() {
  const messages = [{ role: 'user', content: "What is the temperature in New York?" }]

  while (true) {
    const stream = await ollama.chat({
      model: 'qwen3',
      messages,
      tools: [getTemperatureTool],
      stream: true,
      think: true,
    })

    let thinking = ''
    let content = ''
    const toolCalls: any[] = []
    let doneThinking = false

    for await (const chunk of stream) {
      if (chunk.message.thinking) {
        thinking += chunk.message.thinking
        process.stdout.write(chunk.message.thinking)
      }
      if (chunk.message.content) {
        if (!doneThinking) {
          doneThinking = true
          process.stdout.write('\n')
        }
        content += chunk.message.content
        process.stdout.write(chunk.message.content)
      }
      if (chunk.message.tool_calls?.length) {
        toolCalls.push(...chunk.message.tool_calls)
        console.log(chunk.message.tool_calls)
      }
    }

    if (thinking || content || toolCalls.length) {
      messages.push({ role: 'assistant', thinking, content, tool_calls: toolCalls } as any)
    }

    if (!toolCalls.length) {
      break
    }

    for (const call of toolCalls) {
      if (call.function.name === 'get_temperature') {
        const args = call.function.arguments as { city: string }
        const result = getTemperature(args.city)
        messages.push({ role: 'tool', tool_name: call.function.name, content: result } )
      } else {
        messages.push({ role: 'tool', tool_name: call.function.name, content: 'Unknown tool' } )
      }
    }
  }
}

agentLoop().catch(console.error)

```

This loop streams the assistant response, accumulates partial fields, passes them back together, and appends the tool results so the model can complete its answer.
##
[​](https://docs.ollama.com/capabilities/tool-calling#using-functions-as-tools-with-ollama-python-sdk)
Using functions as tools with Ollama Python SDK
The Python SDK automatically parses functions as a tool schema so we can pass them directly. Schemas can still be passed if needed.

```
from ollama import chat

def get_temperature(city: str) -> str:
  """Get the current temperature for a city

  Args:
    city: The name of the city

  Returns:
    The current temperature for the city
  """
  temperatures = {
    'New York': '22°C',
    'London': '15°C',
  }
  return temperatures.get(city, 'Unknown')

available_functions = {
  'get_temperature': get_temperature,
}
# directly pass the function as part of the tools list
response = chat(model='qwen3', messages=messages, tools=available_functions.values(), think=True)

```

[Previous](https://docs.ollama.com/capabilities/embeddings)[ Web search Next ](https://docs.ollama.com/capabilities/web-search)
⌘I
On this page
  * [Calling a single tool](https://docs.ollama.com/capabilities/tool-calling#calling-a-single-tool)
  * [Parallel tool calling](https://docs.ollama.com/capabilities/tool-calling#parallel-tool-calling)
  * [Multi-turn tool calling (Agent loop)](https://docs.ollama.com/capabilities/tool-calling#multi-turn-tool-calling-agent-loop)
  * [Tool calling with streaming](https://docs.ollama.com/capabilities/tool-calling#tool-calling-with-streaming)
  * [Using functions as tools with Ollama Python SDK](https://docs.ollama.com/capabilities/tool-calling#using-functions-as-tools-with-ollama-python-sdk)


--- DOCUMENT: https://docs.ollama.com/capabilities/vision ---
# Vision
Copy page
Copy page
Vision models accept images alongside text so the model can describe, classify, and answer questions about what it sees.
##
[​](https://docs.ollama.com/capabilities/vision#quick-start)
Quick start

```
ollama run gemma3 ./image.png whats in this image?

```

##
[​](https://docs.ollama.com/capabilities/vision#usage-with-ollama%E2%80%99s-api)
Usage with Ollama’s API
Provide an `images` array. SDKs accept file paths, URLs or raw bytes while the REST API expects base64-encoded image data.
  * cURL
  * Python
  * JavaScript


```
# 1. Download a sample image
curl -L -o test.jpg "https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg"

# 2. Encode the image
IMG=$(base64 < test.jpg | tr -d '\n')

# 3. Send it to Ollama
curl -X POST http://localhost:11434/api/chat \
-H "Content-Type: application/json" \
-d '{
    "model": "gemma3",
    "messages": [{
    "role": "user",
    "content": "What is in this image?",
    "images": ["'"$IMG"'"]
    }],
    "stream": false
}'

```


```
from ollama import chat
# from pathlib import Path

# Pass in the path to the image
path = input('Please enter the path to the image: ')

# You can also pass in base64 encoded image data
# img = base64.b64encode(Path(path).read_bytes()).decode()
# or the raw bytes
# img = Path(path).read_bytes()

response = chat(
  model='gemma3',
  messages=[
    {
      'role': 'user',
      'content': 'What is in this image? Be concise.',
      'images': [path],
    }
  ],
)

print(response.message.content)

```


```
import ollama from 'ollama'

const imagePath = '/absolute/path/to/image.jpg'
const response = await ollama.chat({
  model: 'gemma3',
  messages: [
    { role: 'user', content: 'What is in this image?', images: [imagePath] }
  ],
  stream: false,
})

console.log(response.message.content)

```

[Previous](https://docs.ollama.com/capabilities/structured-outputs)[ EmbeddingsGenerate text embeddings for semantic search, retrieval, and RAG. Next ](https://docs.ollama.com/capabilities/embeddings)
⌘I
On this page
  * [Quick start](https://docs.ollama.com/capabilities/vision#quick-start)
  * [Usage with Ollama’s API](https://docs.ollama.com/capabilities/vision#usage-with-ollama%E2%80%99s-api)


--- DOCUMENT: https://docs.ollama.com/capabilities/web-search ---
# Web search
Copy page
Copy page
Ollama’s web search API can be used to augment models with the latest information to reduce hallucinations and improve accuracy. Web search is provided as a REST API with deeper tool integrations in the Python and JavaScript libraries. This also enables models like OpenAI’s gpt-oss models to conduct long-running research tasks.
##
[​](https://docs.ollama.com/capabilities/web-search#authentication)
Authentication
For access to Ollama’s web search API, create an [API key](https://ollama.com/settings/keys). A free Ollama account is required.
##
[​](https://docs.ollama.com/capabilities/web-search#web-search-api)
Web search API
Performs a web search for a single query and returns relevant results.
###
[​](https://docs.ollama.com/capabilities/web-search#request)
Request
`POST https://ollama.com/api/web_search`
  * `query` (string, required): the search query string
  * `max_results` (integer, optional): maximum results to return (default 5, max 10)


###
[​](https://docs.ollama.com/capabilities/web-search#response)
Response
Returns an object containing:
  * `results` (array): array of search result objects, each containing:
    * `title` (string): the title of the web page
    * `url` (string): the URL of the web page
    * `content` (string): relevant content snippet from the web page


###
[​](https://docs.ollama.com/capabilities/web-search#examples)
Examples
Ensure OLLAMA_API_KEY is set or it must be passed in the Authorization header.
####
[​](https://docs.ollama.com/capabilities/web-search#curl-request)
cURL Request

```
curl https://ollama.com/api/web_search \
  --header "Authorization: Bearer $OLLAMA_API_KEY" \
	-d '{
	  "query":"what is ollama?"
	}'

```

**Response**

```
{
  "results": [
    {
      "title": "Ollama",
      "url": "https://ollama.com/",
      "content": "Cloud models are now available..."
    },
    {
      "title": "What is Ollama? Introduction to the AI model management tool",
      "url": "https://www.hostinger.com/tutorials/what-is-ollama",
      "content": "Ariffud M. 6min Read..."
    },
    {
      "title": "Ollama Explained: Transforming AI Accessibility and Language ...",
      "url": "https://www.geeksforgeeks.org/artificial-intelligence/ollama-explained-transforming-ai-accessibility-and-language-processing/",
      "content": "Data Science Data Science Projects Data Analysis..."
    }
  ]
}

```

####
[​](https://docs.ollama.com/capabilities/web-search#python-library)
Python library

```
import ollama
response = ollama.web_search("What is Ollama?")
print(response)

```

**Example output**

```

results = [
    {
        "title": "Ollama",
        "url": "https://ollama.com/",
        "content": "Cloud models are now available in Ollama..."
    },
    {
        "title": "What is Ollama? Features, Pricing, and Use Cases - Walturn",
        "url": "https://www.walturn.com/insights/what-is-ollama-features-pricing-and-use-cases",
        "content": "Our services..."
    },
    {
        "title": "Complete Ollama Guide: Installation, Usage & Code Examples",
        "url": "https://collabnix.com/complete-ollama-guide-installation-usage-code-examples",
        "content": "Join our Discord Server..."
    }
]


```

More Ollama [Python example](https://github.com/ollama/ollama-python/blob/main/examples/web-search.py)
####
[​](https://docs.ollama.com/capabilities/web-search#javascript-library)
JavaScript Library

```
import { Ollama } from "ollama";

const client = new Ollama();
const results = await client.webSearch("what is ollama?");
console.log(JSON.stringify(results, null, 2));

```

**Example output**

```
{
  "results": [
    {
      "title": "Ollama",
      "url": "https://ollama.com/",
      "content": "Cloud models are now available..."
    },
    {
      "title": "What is Ollama? Introduction to the AI model management tool",
      "url": "https://www.hostinger.com/tutorials/what-is-ollama",
      "content": "Ollama is an open-source tool..."
    },
    {
      "title": "Ollama Explained: Transforming AI Accessibility and Language Processing",
      "url": "https://www.geeksforgeeks.org/artificial-intelligence/ollama-explained-transforming-ai-accessibility-and-language-processing/",
      "content": "Ollama is a groundbreaking..."
    }
  ]
}

```

More Ollama [JavaScript example](https://github.com/ollama/ollama-js/blob/main/examples/websearch/websearch-tools.ts)
##
[​](https://docs.ollama.com/capabilities/web-search#web-fetch-api)
Web fetch API
Fetches a single web page by URL and returns its content.
###
[​](https://docs.ollama.com/capabilities/web-search#request-2)
Request
`POST https://ollama.com/api/web_fetch`
  * `url` (string, required): the URL to fetch


###
[​](https://docs.ollama.com/capabilities/web-search#response-2)
Response
Returns an object containing:
  * `title` (string): the title of the web page
  * `content` (string): the main content of the web page
  * `links` (array): array of links found on the page


###
[​](https://docs.ollama.com/capabilities/web-search#examples-2)
Examples
####
[​](https://docs.ollama.com/capabilities/web-search#curl-request-2)
cURL Request

```
curl --request POST \
  --url https://ollama.com/api/web_fetch \
  --header "Authorization: Bearer $OLLAMA_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
      "url": "ollama.com"
  }'

```

**Response**

```
{
  "title": "Ollama",
  "content": "[Cloud models](https://ollama.com/blog/cloud-models) are now available in Ollama...",
  "links": [
    "http://ollama.com/",
    "http://ollama.com/models",
    "https://github.com/ollama/ollama"
  ]


```

####
[​](https://docs.ollama.com/capabilities/web-search#python-sdk)
Python SDK

```
from ollama import web_fetch

result = web_fetch('https://ollama.com')
print(result)

```

**Result**

```
WebFetchResponse(
    title='Ollama',
    content='[Cloud models](https://ollama.com/blog/cloud-models) are now available in Ollama\n\n**Chat & build
with open models**\n\n[Download](https://ollama.com/download) [Explore
models](https://ollama.com/models)\n\nAvailable for macOS, Windows, and Linux',
    links=['https://ollama.com/', 'https://ollama.com/models', 'https://github.com/ollama/ollama']
)

```

####
[​](https://docs.ollama.com/capabilities/web-search#javascript-sdk)
JavaScript SDK

```
import { Ollama } from "ollama";

const client = new Ollama();
const fetchResult = await client.webFetch("https://ollama.com");
console.log(JSON.stringify(fetchResult, null, 2));

```

**Result**

```
{
  "title": "Ollama",
  "content": "[Cloud models](https://ollama.com/blog/cloud-models) are now available in Ollama...",
  "links": [
    "https://ollama.com/",
    "https://ollama.com/models",
    "https://github.com/ollama/ollama"
  ]
}

```

##
[​](https://docs.ollama.com/capabilities/web-search#building-a-search-agent)
Building a search agent
Use Ollama’s web search API as a tool to build a mini search agent. This example uses Alibaba’s Qwen 3 model with 4B parameters.

```
ollama pull qwen3:4b

```


```
from ollama import chat, web_fetch, web_search

available_tools = {'web_search': web_search, 'web_fetch': web_fetch}

messages = [{'role': 'user', 'content': "what is ollama's new engine"}]

while True:
  response = chat(
    model='qwen3:4b',
    messages=messages,
    tools=[web_search, web_fetch],
    think=True
    )
  if response.message.thinking:
    print('Thinking: ', response.message.thinking)
  if response.message.content:
    print('Content: ', response.message.content)
  messages.append(response.message)
  if response.message.tool_calls:
    print('Tool calls: ', response.message.tool_calls)
    for tool_call in response.message.tool_calls:
      function_to_call = available_tools.get(tool_call.function.name)
      if function_to_call:
        args = tool_call.function.arguments
        result = function_to_call(**args)
        print('Result: ', str(result)[:200]+'...')
        # Result is truncated for limited context lengths
        messages.append({'role': 'tool', 'content': str(result)[:2000 * 4], 'tool_name': tool_call.function.name})
      else:
        messages.append({'role': 'tool', 'content': f'Tool {tool_call.function.name} not found', 'tool_name': tool_call.function.name})
  else:
    break

```

**Result**

```
Thinking:  Okay, the user is asking about Ollama's new engine. I need to figure out what they're referring to. Ollama is a company that develops large language models, so maybe they've released a new model or an updated version of their existing engine....

Tool calls:  [ToolCall(function=Function(name='web_search', arguments={'max_results': 3, 'query': 'Ollama new engine'}))]
Result:  results=[WebSearchResult(content='# New model scheduling\n\n## September 23, 2025\n\nOllama now includes a significantly improved model scheduling system. Ahead of running a model, Ollama’s new engine

Thinking:  Okay, the user asked about Ollama's new engine. Let me look at the search results.

First result is from September 23, 2025, talking about new model scheduling. It mentions improved memory management, reduced crashes, better GPU utilization, and multi-GPU performance. Examples show speed improvements and accurate memory reporting. Supported models include gemma3, llama4, qwen3, etc...

Content:  Ollama has introduced two key updates to its engine, both released in 2025:

1. **Enhanced Model Scheduling (September 23, 2025)**
   - **Precision Memory Management**: Exact memory allocation reduces out-of-memory crashes and optimizes GPU utilization.
   - **Performance Gains**: Examples show significant speed improvements (e.g., 85.54 tokens/s vs 52.02 tokens/s) and full GPU layer utilization.
   - **Multi-GPU Support**: Improved efficiency across multiple GPUs, with accurate memory reporting via tools like `nvidia-smi`.
   - **Supported Models**: Includes `gemma3`, `llama4`, `qwen3`, `mistral-small3.2`, and more.

2. **Multimodal Engine (May 15, 2025)**
   - **Vision Support**: First-class support for vision models, including `llama4:scout` (109B parameters), `gemma3`, `qwen2.5vl`, and `mistral-small3.1`.
   - **Multimodal Tasks**: Examples include identifying animals in multiple images, answering location-based questions from videos, and document scanning.

These updates highlight Ollama's focus on efficiency, performance, and expanded capabilities for both text and vision tasks.

```

###
[​](https://docs.ollama.com/capabilities/web-search#context-length-and-agents)
Context length and agents
Web search results can return thousands of tokens. It is recommended to increase the context length of the model to at least ~32000 tokens. Search agents work best with full context length. [Ollama’s cloud models](https://docs.ollama.com/cloud) run at the full context length.
##
[​](https://docs.ollama.com/capabilities/web-search#mcp-server)
MCP Server
You can enable web search in any MCP client through the [Python MCP server](https://github.com/ollama/ollama-python/blob/main/examples/web-search-mcp.py).
###
[​](https://docs.ollama.com/capabilities/web-search#cline)
Cline
Ollama’s web search can be integrated with Cline easily using the MCP server configuration. `Manage MCP Servers` > `Configure MCP Servers` > Add the following configuration:

```
{
  "mcpServers": {
    "web_search_and_fetch": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "path/to/web-search-mcp.py"],
      "env": { "OLLAMA_API_KEY": "your_api_key_here" }
    }
  }
}

```

![Cline MCP Configuration](https://mintcdn.com/ollama-9269c548/lS1IbrlCxMxm029K/images/cline-mcp.png?fit=max&auto=format&n=lS1IbrlCxMxm029K&q=85&s=046239fbe74a8e928752b97b1a8954fa)
###
[​](https://docs.ollama.com/capabilities/web-search#codex)
Codex
Ollama works well with OpenAI’s Codex tool. Add the following configuration to `~/.codex/config.toml`

```
[mcp_servers.web_search]
command = "uv"
args = ["run", "path/to/web-search-mcp.py"]
env = { "OLLAMA_API_KEY" = "your_api_key_here" }

```

![Codex MCP Configuration](https://mintcdn.com/ollama-9269c548/lS1IbrlCxMxm029K/images/codex-mcp.png?fit=max&auto=format&n=lS1IbrlCxMxm029K&q=85&s=775b41bb85af7836b0a5a609de7d1f6f)
###
[​](https://docs.ollama.com/capabilities/web-search#goose)
Goose
Ollama can integrate with Goose via its MCP feature. ![Goose MCP Configuration 1](https://mintcdn.com/ollama-9269c548/lS1IbrlCxMxm029K/images/goose-mcp-1.png?fit=max&auto=format&n=lS1IbrlCxMxm029K&q=85&s=5fea6e0aab7865dc950470f004c549e8) ![Goose MCP Configuration 2](https://mintcdn.com/ollama-9269c548/lS1IbrlCxMxm029K/images/goose-mcp-2.png?fit=max&auto=format&n=lS1IbrlCxMxm029K&q=85&s=c69c12389f7dd60ef1c53cd10af82a7d)
###
[​](https://docs.ollama.com/capabilities/web-search#other-integrations)
Other integrations
Ollama can be integrated into most of the tools available either through direct integration of Ollama’s API, Python / JavaScript libraries, OpenAI compatible API, and MCP server integration.
[Previous](https://docs.ollama.com/capabilities/tool-calling)[ Overview Next ](https://docs.ollama.com/integrations)
⌘I
On this page
  * [Authentication](https://docs.ollama.com/capabilities/web-search#authentication)
  * [Web search API](https://docs.ollama.com/capabilities/web-search#web-search-api)
  * [Request](https://docs.ollama.com/capabilities/web-search#request)
  * [Response](https://docs.ollama.com/capabilities/web-search#response)
  * [Examples](https://docs.ollama.com/capabilities/web-search#examples)
  * [cURL Request](https://docs.ollama.com/capabilities/web-search#curl-request)
  * [Python library](https://docs.ollama.com/capabilities/web-search#python-library)
  * [JavaScript Library](https://docs.ollama.com/capabilities/web-search#javascript-library)
  * [Web fetch API](https://docs.ollama.com/capabilities/web-search#web-fetch-api)
  * [Request](https://docs.ollama.com/capabilities/web-search#request-2)
  * [Response](https://docs.ollama.com/capabilities/web-search#response-2)
  * [Examples](https://docs.ollama.com/capabilities/web-search#examples-2)
  * [cURL Request](https://docs.ollama.com/capabilities/web-search#curl-request-2)
  * [Python SDK](https://docs.ollama.com/capabilities/web-search#python-sdk)
  * [JavaScript SDK](https://docs.ollama.com/capabilities/web-search#javascript-sdk)
  * [Building a search agent](https://docs.ollama.com/capabilities/web-search#building-a-search-agent)
  * [Context length and agents](https://docs.ollama.com/capabilities/web-search#context-length-and-agents)
  * [MCP Server](https://docs.ollama.com/capabilities/web-search#mcp-server)
  * [Cline](https://docs.ollama.com/capabilities/web-search#cline)
  * [Codex](https://docs.ollama.com/capabilities/web-search#codex)
  * [Goose](https://docs.ollama.com/capabilities/web-search#goose)
  * [Other integrations](https://docs.ollama.com/capabilities/web-search#other-integrations)


--- DOCUMENT: https://docs.ollama.com/cli ---
# CLI Reference
Copy page
Copy page
###
[​](https://docs.ollama.com/cli#run-a-model)
Run a model

```
ollama run gemma3

```

###
[​](https://docs.ollama.com/cli#launch-integrations)
Launch integrations

```
ollama launch

```

Configure and launch external applications to use Ollama models. This provides an interactive way to set up and start integrations with supported apps.
####
[​](https://docs.ollama.com/cli#supported-integrations)
Supported integrations
  * **OpenCode** - Open-source coding assistant
  * **Claude Code** - Anthropic’s agentic coding tool
  * **Codex** - OpenAI’s coding assistant
  * **VS Code** - Microsoft’s IDE with built-in AI chat
  * **Droid** - Factory’s AI coding agent


####
[​](https://docs.ollama.com/cli#examples)
Examples
Launch an integration interactively:

```
ollama launch

```

Launch a specific integration:

```
ollama launch claude

```

Launch with a specific model:

```
ollama launch claude --model qwen3.5

```

Configure without launching:

```
ollama launch droid --config

```

####
[​](https://docs.ollama.com/cli#multiline-input)
Multiline input
For multiline input, you can wrap text with `"""`:

```
>>> """Hello,
... world!
... """
I'm a basic program that prints the famous "Hello, world!" message to the console.

```

####
[​](https://docs.ollama.com/cli#multimodal-models)
Multimodal models

```
ollama run gemma3 "What's in this image? /Users/jmorgan/Desktop/smile.png"

```

###
[​](https://docs.ollama.com/cli#generate-embeddings)
Generate embeddings

```
ollama run embeddinggemma "Hello world"

```

Output is a JSON array:

```
echo "Hello world" | ollama run nomic-embed-text

```

###
[​](https://docs.ollama.com/cli#download-a-model)
Download a model

```
ollama pull gemma3

```

###
[​](https://docs.ollama.com/cli#remove-a-model)
Remove a model

```
ollama rm gemma3

```

###
[​](https://docs.ollama.com/cli#list-models)
List models

```
ollama ls

```

###
[​](https://docs.ollama.com/cli#sign-in-to-ollama)
Sign in to Ollama

```
ollama signin

```

###
[​](https://docs.ollama.com/cli#sign-out-of-ollama)
Sign out of Ollama

```
ollama signout

```

###
[​](https://docs.ollama.com/cli#create-a-customized-model)
Create a customized model
First, create a `Modelfile`

```
FROM gemma3
SYSTEM """You are a happy cat."""

```

Then run `ollama create`:

```
ollama create -f Modelfile

```

###
[​](https://docs.ollama.com/cli#list-running-models)
List running models

```
ollama ps

```

###
[​](https://docs.ollama.com/cli#stop-a-running-model)
Stop a running model

```
ollama stop gemma3

```

###
[​](https://docs.ollama.com/cli#start-ollama)
Start Ollama

```
ollama serve

```

To view a list of environment variables that can be set run `ollama serve --help`
[Previous](https://docs.ollama.com/integrations/marimo)[ NemoClaw Next ](https://docs.ollama.com/integrations/nemoclaw)
⌘I
On this page
  * [Run a model](https://docs.ollama.com/cli#run-a-model)
  * [Launch integrations](https://docs.ollama.com/cli#launch-integrations)
  * [Supported integrations](https://docs.ollama.com/cli#supported-integrations)
  * [Examples](https://docs.ollama.com/cli#examples)
  * [Multiline input](https://docs.ollama.com/cli#multiline-input)
  * [Multimodal models](https://docs.ollama.com/cli#multimodal-models)
  * [Generate embeddings](https://docs.ollama.com/cli#generate-embeddings)
  * [Download a model](https://docs.ollama.com/cli#download-a-model)
  * [Remove a model](https://docs.ollama.com/cli#remove-a-model)
  * [List models](https://docs.ollama.com/cli#list-models)
  * [Sign in to Ollama](https://docs.ollama.com/cli#sign-in-to-ollama)
  * [Sign out of Ollama](https://docs.ollama.com/cli#sign-out-of-ollama)
  * [Create a customized model](https://docs.ollama.com/cli#create-a-customized-model)
  * [List running models](https://docs.ollama.com/cli#list-running-models)
  * [Stop a running model](https://docs.ollama.com/cli#stop-a-running-model)
  * [Start Ollama](https://docs.ollama.com/cli#start-ollama)


--- DOCUMENT: https://docs.ollama.com/cloud ---
# Cloud
Copy page
Copy page
##
[​](https://docs.ollama.com/cloud#cloud-models)
Cloud Models
Ollama’s cloud models are a new kind of model in Ollama that can run without a powerful GPU. Instead, cloud models are automatically offloaded to Ollama’s cloud service while offering the same capabilities as local models, making it possible to keep using your local tools while running larger models that wouldn’t fit on a personal computer.
###
[​](https://docs.ollama.com/cloud#supported-models)
Supported models
For a list of supported models, see Ollama’s [model library](https://ollama.com/search?c=cloud).
###
[​](https://docs.ollama.com/cloud#running-cloud-models)
Running Cloud models
Ollama’s cloud models require an account on [ollama.com](https://ollama.com). To sign in or create an account, run:

```
ollama signin

```

  * CLI
  * Python
  * JavaScript
  * cURL


To run a cloud model, open the terminal and run:

```
ollama run gpt-oss:120b-cloud

```

First, pull a cloud model so it can be accessed:

```
ollama pull gpt-oss:120b-cloud

```

Next, install [Ollama’s Python library](https://github.com/ollama/ollama-python):

```
pip install ollama

```

Next, create and run a simple Python script:

```
from ollama import Client

client = Client()

messages = [
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
]

for part in client.chat('gpt-oss:120b-cloud', messages=messages, stream=True):
  print(part['message']['content'], end='', flush=True)

```

First, pull a cloud model so it can be accessed:

```
ollama pull gpt-oss:120b-cloud

```

Next, install [Ollama’s JavaScript library](https://github.com/ollama/ollama-js):

```
npm i ollama

```

Then use the library to run a cloud model:

```
import { Ollama } from "ollama";

const ollama = new Ollama();

const response = await ollama.chat({
  model: "gpt-oss:120b-cloud",
  messages: [{ role: "user", content: "Explain quantum computing" }],
  stream: true,
});

for await (const part of response) {
  process.stdout.write(part.message.content);
}

```

First, pull a cloud model so it can be accessed:

```
ollama pull gpt-oss:120b-cloud

```

Run the following cURL command to run the command via Ollama’s API:

```
curl http://localhost:11434/api/chat -d '{
  "model": "gpt-oss:120b-cloud",
  "messages": [{
    "role": "user",
    "content": "Why is the sky blue?"
  }],
  "stream": false
}'

```

##
[​](https://docs.ollama.com/cloud#cloud-api-access)
Cloud API access
Cloud models can also be accessed directly on ollama.com’s API. In this mode, ollama.com acts as a remote Ollama host.
###
[​](https://docs.ollama.com/cloud#authentication)
Authentication
For direct access to ollama.com’s API, first create an [API key](https://ollama.com/settings/keys). Then, set the `OLLAMA_API_KEY` environment variable to your API key.

```
export OLLAMA_API_KEY=your_api_key

```

###
[​](https://docs.ollama.com/cloud#listing-models)
Listing models
For models available directly via Ollama’s API, models can be listed via:

```
curl https://ollama.com/api/tags

```

###
[​](https://docs.ollama.com/cloud#generating-a-response)
Generating a response
  * Python
  * JavaScript
  * cURL


First, install [Ollama’s Python library](https://github.com/ollama/ollama-python)

```
pip install ollama

```

Then make a request

```
import os
from ollama import Client

client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
)

messages = [
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
]

for part in client.chat('gpt-oss:120b', messages=messages, stream=True):
  print(part['message']['content'], end='', flush=True)

```

First, install [Ollama’s JavaScript library](https://github.com/ollama/ollama-js):

```
npm i ollama

```

Next, make a request to the model:

```
import { Ollama } from "ollama";

const ollama = new Ollama({
  host: "https://ollama.com",
  headers: {
    Authorization: "Bearer " + process.env.OLLAMA_API_KEY,
  },
});

const response = await ollama.chat({
  model: "gpt-oss:120b",
  messages: [{ role: "user", content: "Explain quantum computing" }],
  stream: true,
});

for await (const part of response) {
  process.stdout.write(part.message.content);
}

```

Generate a response via Ollama’s chat API:

```
curl https://ollama.com/api/chat \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -d '{
    "model": "gpt-oss:120b",
    "messages": [{
      "role": "user",
      "content": "Why is the sky blue?"
    }],
    "stream": false
  }'

```

##
[​](https://docs.ollama.com/cloud#local-only)
Local only
Ollama can run in local-only mode by [disabling Ollama’s cloud](https://docs.ollama.com/faq#how-do-i-disable-ollama-cloud) features.
[Previous](https://docs.ollama.com/quickstart)[ Streaming Next ](https://docs.ollama.com/capabilities/streaming)
⌘I
On this page
  * [Cloud Models](https://docs.ollama.com/cloud#cloud-models)
  * [Supported models](https://docs.ollama.com/cloud#supported-models)
  * [Running Cloud models](https://docs.ollama.com/cloud#running-cloud-models)
  * [Cloud API access](https://docs.ollama.com/cloud#cloud-api-access)
  * [Authentication](https://docs.ollama.com/cloud#authentication)
  * [Listing models](https://docs.ollama.com/cloud#listing-models)
  * [Generating a response](https://docs.ollama.com/cloud#generating-a-response)
  * [Local only](https://docs.ollama.com/cloud#local-only)


--- DOCUMENT: https://docs.ollama.com/context-length ---
# Context length
Copy page
Copy page
Context length is the maximum number of tokens that the model has access to in memory.
Ollama defaults to the following context lengths based on VRAM:
  * < 24 GiB VRAM: 4k context
  * 24-48 GiB VRAM: 32k context
  * >= 48 GiB VRAM: 256k context


Tasks which require large context like web search, agents, and coding tools should be set to at least 64000 tokens.
##
[​](https://docs.ollama.com/context-length#setting-context-length)
Setting context length
Setting a larger context length will increase the amount of memory required to run a model. Ensure you have enough VRAM available to increase the context length. Cloud models are set to their maximum context length by default.
###
[​](https://docs.ollama.com/context-length#app)
App
Change the slider in the Ollama app under settings to your desired context length. ![Context length in Ollama app](https://mintcdn.com/ollama-9269c548/SjntZZpXgbN5v4M5/images/ollama-settings.png?fit=max&auto=format&n=SjntZZpXgbN5v4M5&q=85&s=e8a7ccd30fd9cee5e93662db05b43dc7)
###
[​](https://docs.ollama.com/context-length#cli)
CLI
If editing the context length for Ollama is not possible, the context length can also be updated when serving Ollama.

```
OLLAMA_CONTEXT_LENGTH=64000 ollama serve

```

###
[​](https://docs.ollama.com/context-length#check-allocated-context-length-and-model-offloading)
Check allocated context length and model offloading
For best performance, use the maximum context length for a model, and avoid offloading the model to CPU. Verify the split under `PROCESSOR` using `ollama ps`.

```
ollama ps

```


```
NAME             ID              SIZE      PROCESSOR    CONTEXT    UNTIL
gemma3:latest    a2af6cc3eb7f    6.6 GB    100% GPU     65536      2 minutes from now

```

[Previous](https://docs.ollama.com/modelfile)[ Linux Next ](https://docs.ollama.com/linux)
⌘I
On this page
  * [Setting context length](https://docs.ollama.com/context-length#setting-context-length)
  * [App](https://docs.ollama.com/context-length#app)
  * [CLI](https://docs.ollama.com/context-length#cli)
  * [Check allocated context length and model offloading](https://docs.ollama.com/context-length#check-allocated-context-length-and-model-offloading)


![Context length in Ollama app](https://mintcdn.com/ollama-9269c548/SjntZZpXgbN5v4M5/images/ollama-settings.png?w=840&fit=max&auto=format&n=SjntZZpXgbN5v4M5&q=85&s=7c7314c5f77798307a93ff466501d1cc)


--- DOCUMENT: https://docs.ollama.com/docker ---
# Docker
Copy page
Copy page
##
[​](https://docs.ollama.com/docker#cpu-only)
CPU only

```
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

```

##
[​](https://docs.ollama.com/docker#nvidia-gpu)
Nvidia GPU
Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installation).
###
[​](https://docs.ollama.com/docker#install-with-apt)
Install with Apt
  1. Configure the repository

```
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
    | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update

```

  2. Install the NVIDIA Container Toolkit packages

```
sudo apt-get install -y nvidia-container-toolkit

```


###
[​](https://docs.ollama.com/docker#install-with-yum-or-dnf)
Install with Yum or Dnf
  1. Configure the repository

```
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo \
    | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo

```

  2. Install the NVIDIA Container Toolkit packages

```
sudo yum install -y nvidia-container-toolkit

```


###
[​](https://docs.ollama.com/docker#configure-docker-to-use-nvidia-driver)
Configure Docker to use Nvidia driver

```
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

```

###
[​](https://docs.ollama.com/docker#start-the-container)
Start the container

```
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

```

If you’re running on an NVIDIA JetPack system, Ollama can’t automatically discover the correct JetPack version. Pass the environment variable `JETSON_JETPACK=5` or `JETSON_JETPACK=6` to the container to select version 5 or 6.
##
[​](https://docs.ollama.com/docker#amd-gpu)
AMD GPU
To run Ollama using Docker with AMD GPUs, use the `rocm` tag and the following command:

```
docker run -d --device /dev/kfd --device /dev/dri -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama:rocm

```

##
[​](https://docs.ollama.com/docker#vulkan-support)
Vulkan Support
Vulkan is bundled into the `ollama/ollama` image.

```
docker run -d --device /dev/kfd --device /dev/dri -v ollama:/root/.ollama -p 11434:11434 -e OLLAMA_VULKAN=1 --name ollama ollama/ollama

```

##
[​](https://docs.ollama.com/docker#run-model-locally)
Run model locally
Now you can run a model:

```
docker exec -it ollama ollama run llama3.2

```

##
[​](https://docs.ollama.com/docker#try-different-models)
Try different models
More models can be found on the [Ollama library](https://ollama.com/library).
[Previous](https://docs.ollama.com/windows)[ Importing a Model Next ](https://docs.ollama.com/import)
⌘I
On this page
  * [CPU only](https://docs.ollama.com/docker#cpu-only)
  * [Nvidia GPU](https://docs.ollama.com/docker#nvidia-gpu)
  * [Install with Apt](https://docs.ollama.com/docker#install-with-apt)
  * [Install with Yum or Dnf](https://docs.ollama.com/docker#install-with-yum-or-dnf)
  * [Configure Docker to use Nvidia driver](https://docs.ollama.com/docker#configure-docker-to-use-nvidia-driver)
  * [Start the container](https://docs.ollama.com/docker#start-the-container)
  * [AMD GPU](https://docs.ollama.com/docker#amd-gpu)
  * [Vulkan Support](https://docs.ollama.com/docker#vulkan-support)
  * [Run model locally](https://docs.ollama.com/docker#run-model-locally)
  * [Try different models](https://docs.ollama.com/docker#try-different-models)


--- DOCUMENT: https://docs.ollama.com/faq ---
# FAQ
Copy page
Copy page
##
[​](https://docs.ollama.com/faq#how-can-i-upgrade-ollama)
How can I upgrade Ollama?
Ollama on macOS and Windows will automatically download updates. Click on the taskbar or menubar item and then click “Restart to update” to apply the update. Updates can also be installed by downloading the latest version [manually](https://ollama.com/download/). On Linux, re-run the install script:

```
curl -fsSL https://ollama.com/install.sh | sh

```

##
[​](https://docs.ollama.com/faq#how-can-i-view-the-logs)
How can I view the logs?
Review the [Troubleshooting](https://docs.ollama.com/troubleshooting.mdx) docs for more about using logs.
##
[​](https://docs.ollama.com/faq#is-my-gpu-compatible-with-ollama)
Is my GPU compatible with Ollama?
Please refer to the [GPU docs](https://docs.ollama.com/gpu.mdx).
##
[​](https://docs.ollama.com/faq#how-can-i-specify-the-context-window-size)
How can I specify the context window size?
By default, Ollama uses a context window size of 4096 tokens. This can be overridden with the `OLLAMA_CONTEXT_LENGTH` environment variable. For example, to set the default context window to 8K, use:

```
OLLAMA_CONTEXT_LENGTH=8192 ollama serve

```

To change this when using `ollama run`, use `/set parameter`:

```
/set parameter num_ctx 4096

```

When using the API, specify the `num_ctx` parameter:

```
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?",
  "options": {
    "num_ctx": 4096
  }
}'

```

##
[​](https://docs.ollama.com/faq#how-can-i-tell-if-my-model-was-loaded-onto-the-gpu)
How can I tell if my model was loaded onto the GPU?
Use the `ollama ps` command to see what models are currently loaded into memory.

```
ollama ps

```

**Output** :

```
NAME        ID            SIZE    PROCESSOR   UNTIL
llama3:70b  bcfb190ca3a7  42 GB   100% GPU    4 minutes from now

```

The `Processor` column will show which memory the model was loaded into:
  * `100% GPU` means the model was loaded entirely into the GPU
  * `100% CPU` means the model was loaded entirely in system memory
  * `48%/52% CPU/GPU` means the model was loaded partially onto both the GPU and into system memory


##
[​](https://docs.ollama.com/faq#how-do-i-configure-ollama-server)
How do I configure Ollama server?
Ollama server can be configured with environment variables.
###
[​](https://docs.ollama.com/faq#setting-environment-variables-on-mac)
Setting environment variables on Mac
If Ollama is run as a macOS application, environment variables should be set using `launchctl`:
  1. For each environment variable, call `launchctl setenv`.

```
launchctl setenv OLLAMA_HOST "0.0.0.0:11434"

```

  2. Restart Ollama application.


###
[​](https://docs.ollama.com/faq#setting-environment-variables-on-linux)
Setting environment variables on Linux
If Ollama is run as a systemd service, environment variables should be set using `systemctl`:
  1. Edit the systemd service by calling `systemctl edit ollama.service`. This will open an editor.
  2. For each environment variable, add a line `Environment` under section `[Service]`:

```
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"

```

  3. Save and exit.
  4. Reload `systemd` and restart Ollama:

```
systemctl daemon-reload
systemctl restart ollama

```


###
[​](https://docs.ollama.com/faq#setting-environment-variables-on-windows)
Setting environment variables on Windows
On Windows, Ollama inherits your user and system environment variables.
  1. First Quit Ollama by clicking on it in the task bar.
  2. Start the Settings (Windows 11) or Control Panel (Windows 10) application and search for _environment variables_.
  3. Click on _Edit environment variables for your account_.
  4. Edit or create a new variable for your user account for `OLLAMA_HOST`, `OLLAMA_MODELS`, etc.
  5. Click OK/Apply to save.
  6. Start the Ollama application from the Windows Start menu.


##
[​](https://docs.ollama.com/faq#how-do-i-use-ollama-behind-a-proxy)
How do I use Ollama behind a proxy?
Ollama pulls models from the Internet and may require a proxy server to access the models. Use `HTTPS_PROXY` to redirect outbound requests through the proxy. Ensure the proxy certificate is installed as a system certificate. Refer to the section above for how to use environment variables on your platform.
Avoid setting `HTTP_PROXY`. Ollama does not use HTTP for model pulls, only HTTPS. Setting `HTTP_PROXY` may interrupt client connections to the server.
###
[​](https://docs.ollama.com/faq#how-do-i-use-ollama-behind-a-proxy-in-docker)
How do I use Ollama behind a proxy in Docker?
The Ollama Docker container image can be configured to use a proxy by passing `-e HTTPS_PROXY=https://proxy.example.com` when starting the container. Alternatively, the Docker daemon can be configured to use a proxy. Instructions are available for Docker Desktop on [macOS](https://docs.docker.com/desktop/settings/mac/#proxies), [Windows](https://docs.docker.com/desktop/settings/windows/#proxies), and [Linux](https://docs.docker.com/desktop/settings/linux/#proxies), and Docker [daemon with systemd](https://docs.docker.com/config/daemon/systemd/#httphttps-proxy). Ensure the certificate is installed as a system certificate when using HTTPS. This may require a new Docker image when using a self-signed certificate.

```
FROM ollama/ollama
COPY my-ca.pem /usr/local/share/ca-certificates/my-ca.crt
RUN update-ca-certificates

```

Build and run this image:

```
docker build -t ollama-with-ca .
docker run -d -e HTTPS_PROXY=https://my.proxy.example.com -p 11434:11434 ollama-with-ca

```

##
[​](https://docs.ollama.com/faq#does-ollama-send-my-prompts-and-answers-back-to-ollama-com)
Does Ollama send my prompts and answers back to ollama.com?
Ollama runs locally. We don’t see your prompts or data when you run locally. When using cloud-hosted models, we process your prompts and responses to provide the service but do not store or log that content and never train on it. We collect basic account info and limited usage metadata to provide the service that does not include prompt or response content. We don’t sell your data. You can delete your account anytime.
##
[​](https://docs.ollama.com/faq#how-do-i-disable-ollama%E2%80%99s-cloud-features)
How do I disable Ollama’s cloud features?
Ollama can run in local only mode by disabling Ollama’s cloud features. By turning off Ollama’s cloud features, you will lose the ability to use Ollama’s cloud models and web search. Set `disable_ollama_cloud` in `~/.ollama/server.json`:

```
{
  "disable_ollama_cloud": true
}

```

You can also set the environment variable:

```
OLLAMA_NO_CLOUD=1

```

Restart Ollama after changing configuration. Once disabled, Ollama’s logs will show `Ollama cloud disabled: true`.
##
[​](https://docs.ollama.com/faq#how-can-i-expose-ollama-on-my-network)
How can I expose Ollama on my network?
Ollama binds 127.0.0.1 port 11434 by default. Change the bind address with the `OLLAMA_HOST` environment variable. Refer to the section [above](https://docs.ollama.com/faq#how-do-i-configure-ollama-server) for how to set environment variables on your platform.
##
[​](https://docs.ollama.com/faq#how-can-i-use-ollama-with-a-proxy-server)
How can I use Ollama with a proxy server?
Ollama runs an HTTP server and can be exposed using a proxy server such as Nginx. To do so, configure the proxy to forward requests and optionally set required headers (if not exposing Ollama on the network). For example, with Nginx:

```
server {
    listen 80;
    server_name example.com;  # Replace with your domain or IP
    location / {
        proxy_pass http://localhost:11434;
        proxy_set_header Host localhost:11434;
    }
}

```

##
[​](https://docs.ollama.com/faq#how-can-i-use-ollama-with-ngrok)
How can I use Ollama with ngrok?
Ollama can be accessed using a range of tunneling apps. For example with Ngrok:

```
ngrok http 11434 --host-header="localhost:11434"

```

##
[​](https://docs.ollama.com/faq#how-can-i-use-ollama-with-cloudflare-tunnel)
How can I use Ollama with Cloudflare Tunnel?
To use Ollama with Cloudflare Tunnel, use the `--url` and `--http-host-header` flags:

```
cloudflared tunnel --url http://localhost:11434 --http-host-header="localhost:11434"

```

##
[​](https://docs.ollama.com/faq#how-can-i-allow-additional-web-origins-to-access-ollama)
How can I allow additional web origins to access Ollama?
Ollama allows cross-origin requests from `127.0.0.1` and `0.0.0.0` by default. Additional origins can be configured with `OLLAMA_ORIGINS`. For browser extensions, you’ll need to explicitly allow the extension’s origin pattern. Set `OLLAMA_ORIGINS` to include `chrome-extension://*`, `moz-extension://*`, and `safari-web-extension://*` if you wish to allow all browser extensions access, or specific extensions as needed:

```
# Allow all Chrome, Firefox, and Safari extensions
OLLAMA_ORIGINS=chrome-extension://*,moz-extension://*,safari-web-extension://* ollama serve

```

Refer to the section [above](https://docs.ollama.com/faq#how-do-i-configure-ollama-server) for how to set environment variables on your platform.
##
[​](https://docs.ollama.com/faq#where-are-models-stored)
Where are models stored?
  * macOS: `~/.ollama/models`
  * Linux: `/usr/share/ollama/.ollama/models`
  * Windows: `C:\Users\%username%\.ollama\models`


###
[​](https://docs.ollama.com/faq#how-do-i-set-them-to-a-different-location)
How do I set them to a different location?
If a different directory needs to be used, set the environment variable `OLLAMA_MODELS` to the chosen directory.
On Linux using the standard installer, the `ollama` user needs read and write access to the specified directory. To assign the directory to the `ollama` user run `sudo chown -R ollama:ollama <directory>`.
Refer to the section [above](https://docs.ollama.com/faq#how-do-i-configure-ollama-server) for how to set environment variables on your platform.
##
[​](https://docs.ollama.com/faq#how-can-i-use-ollama-in-visual-studio-code)
How can I use Ollama in Visual Studio Code?
There is already a large collection of plugins available for VS Code as well as other editors that leverage Ollama. See the list of [extensions & plugins](https://github.com/ollama/ollama#extensions--plugins) at the bottom of the main repository readme.
##
[​](https://docs.ollama.com/faq#how-do-i-use-ollama-with-gpu-acceleration-in-docker)
How do I use Ollama with GPU acceleration in Docker?
The Ollama Docker container can be configured with GPU acceleration in Linux or Windows (with WSL2). This requires the [nvidia-container-toolkit](https://github.com/NVIDIA/nvidia-container-toolkit). See [ollama/ollama](https://hub.docker.com/r/ollama/ollama) for more details. GPU acceleration is not available for Docker Desktop in macOS due to the lack of GPU passthrough and emulation.
##
[​](https://docs.ollama.com/faq#why-is-networking-slow-in-wsl2-on-windows-10)
Why is networking slow in WSL2 on Windows 10?
This can impact both installing Ollama, as well as downloading models. Open `Control Panel > Networking and Internet > View network status and tasks` and click on `Change adapter settings` on the left panel. Find the `vEthernet (WSL)` adapter, right click and select `Properties`. Click on `Configure` and open the `Advanced` tab. Search through each of the properties until you find `Large Send Offload Version 2 (IPv4)` and `Large Send Offload Version 2 (IPv6)`. _Disable_ both of these properties.
##
[​](https://docs.ollama.com/faq#how-can-i-preload-a-model-into-ollama-to-get-faster-response-times)
How can I preload a model into Ollama to get faster response times?
If you are using the API you can preload a model by sending the Ollama server an empty request. This works with both the `/api/generate` and `/api/chat` API endpoints. To preload the mistral model using the generate endpoint, use:

```
curl http://localhost:11434/api/generate -d '{"model": "mistral"}'

```

To use the chat completions endpoint, use:

```
curl http://localhost:11434/api/chat -d '{"model": "mistral"}'

```

To preload a model using the CLI, use the command:

```
ollama run llama3.2 ""

```

##
[​](https://docs.ollama.com/faq#how-do-i-keep-a-model-loaded-in-memory-or-make-it-unload-immediately)
How do I keep a model loaded in memory or make it unload immediately?
By default models are kept in memory for 5 minutes before being unloaded. This allows for quicker response times if you’re making numerous requests to the LLM. If you want to immediately unload a model from memory, use the `ollama stop` command:

```
ollama stop llama3.2

```

If you’re using the API, use the `keep_alive` parameter with the `/api/generate` and `/api/chat` endpoints to set the amount of time that a model stays in memory. The `keep_alive` parameter can be set to:
  * a duration string (such as “10m” or “24h”)
  * a number in seconds (such as 3600)
  * any negative number which will keep the model loaded in memory (e.g. -1 or “-1m”)
  * ‘0’ which will unload the model immediately after generating a response

For example, to preload a model and leave it in memory use:

```
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "keep_alive": -1}'

```

To unload the model and free up memory use:

```
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "keep_alive": 0}'

```

Alternatively, you can change the amount of time all models are loaded into memory by setting the `OLLAMA_KEEP_ALIVE` environment variable when starting the Ollama server. The `OLLAMA_KEEP_ALIVE` variable uses the same parameter types as the `keep_alive` parameter types mentioned above. Refer to the section explaining [how to configure the Ollama server](https://docs.ollama.com/faq#how-do-i-configure-ollama-server) to correctly set the environment variable. The `keep_alive` API parameter with the `/api/generate` and `/api/chat` API endpoints will override the `OLLAMA_KEEP_ALIVE` setting.
##
[​](https://docs.ollama.com/faq#how-do-i-manage-the-maximum-number-of-requests-the-ollama-server-can-queue)
How do I manage the maximum number of requests the Ollama server can queue?
If too many requests are sent to the server, it will respond with a 503 error indicating the server is overloaded. You can adjust how many requests may be queued by setting `OLLAMA_MAX_QUEUE`.
##
[​](https://docs.ollama.com/faq#how-does-ollama-handle-concurrent-requests)
How does Ollama handle concurrent requests?
Ollama supports two levels of concurrent processing. If your system has sufficient available memory (system memory when using CPU inference, or VRAM for GPU inference) then multiple models can be loaded at the same time. For a given model, if there is sufficient available memory when the model is loaded, it is configured to allow parallel request processing. If there is insufficient available memory to load a new model request while one or more models are already loaded, all new requests will be queued until the new model can be loaded. As prior models become idle, one or more will be unloaded to make room for the new model. Queued requests will be processed in order. When using GPU inference new models must be able to completely fit in VRAM to allow concurrent model loads. Parallel request processing for a given model results in increasing the context size by the number of parallel requests. For example, a 2K context with 4 parallel requests will result in an 8K context and additional memory allocation. The following server settings may be used to adjust how Ollama handles concurrent requests on most platforms:
  * `OLLAMA_MAX_LOADED_MODELS` - The maximum number of models that can be loaded concurrently provided they fit in available memory. The default is 3 * the number of GPUs or 3 for CPU inference.
  * `OLLAMA_NUM_PARALLEL` - The maximum number of parallel requests each model will process at the same time, default 1. Required RAM will scale by `OLLAMA_NUM_PARALLEL` * `OLLAMA_CONTEXT_LENGTH`.
  * `OLLAMA_MAX_QUEUE` - The maximum number of requests Ollama will queue when busy before rejecting additional requests. The default is 512

Note: Windows with Radeon GPUs currently default to 1 model maximum due to limitations in ROCm v5.7 for available VRAM reporting. Once ROCm v6.2 is available, Windows Radeon will follow the defaults above. You may enable concurrent model loads on Radeon on Windows, but ensure you don’t load more models than will fit into your GPU’s VRAM.
##
[​](https://docs.ollama.com/faq#how-does-ollama-load-models-on-multiple-gpus)
How does Ollama load models on multiple GPUs?
When loading a new model, Ollama evaluates the required VRAM for the model against what is currently available. If the model will entirely fit on any single GPU, Ollama will load the model on that GPU. This typically provides the best performance as it reduces the amount of data transferring across the PCI bus during inference. If the model does not fit entirely on one GPU, then it will be spread across all the available GPUs.
##
[​](https://docs.ollama.com/faq#how-can-i-enable-flash-attention)
How can I enable Flash Attention?
Flash Attention is a feature of most modern models that can significantly reduce memory usage as the context size grows. To enable Flash Attention, set the `OLLAMA_FLASH_ATTENTION` environment variable to `1` when starting the Ollama server.
##
[​](https://docs.ollama.com/faq#how-can-i-set-the-quantization-type-for-the-k/v-cache)
How can I set the quantization type for the K/V cache?
The K/V context cache can be quantized to significantly reduce memory usage when Flash Attention is enabled. To use quantized K/V cache with Ollama you can set the following environment variable:
  * `OLLAMA_KV_CACHE_TYPE` - The quantization type for the K/V cache. Default is `f16`.


Currently this is a global option - meaning all models will run with the specified quantization type.
The currently available K/V cache quantization types are:
  * `f16` - high precision and memory usage (default).
  * `q8_0` - 8-bit quantization, uses approximately 1/2 the memory of `f16` with a very small loss in precision, this usually has no noticeable impact on the model’s quality (recommended if not using f16).
  * `q4_0` - 4-bit quantization, uses approximately 1/4 the memory of `f16` with a small-medium loss in precision that may be more noticeable at higher context sizes.

How much the cache quantization impacts the model’s response quality will depend on the model and the task. Models that have a high GQA count (e.g. Qwen2) may see a larger impact on precision from quantization than models with a low GQA count. You may need to experiment with different quantization types to find the best balance between memory usage and quality.
##
[​](https://docs.ollama.com/faq#where-can-i-find-my-ollama-public-key)
Where can I find my Ollama Public Key?
Your **Ollama Public Key** is the public part of the key pair that lets your local Ollama instance talk to [ollama.com](https://ollama.com). You’ll need it to:
  * Push models to Ollama
  * Pull private models from Ollama to your machine
  * Run models hosted in [Ollama Cloud](https://ollama.com/cloud)


###
[​](https://docs.ollama.com/faq#how-to-add-the-key)
How to Add the Key
  * **Sign-in via the Settings page** in the **Mac** and **Windows App**
  * **Sign‑in via CLI**


```
ollama signin

```

  * **Manually copy & paste** the key on the **Ollama Keys** page: <https://ollama.com/settings/keys>


###
[​](https://docs.ollama.com/faq#where-the-ollama-public-key-lives)
Where the Ollama Public Key lives
| OS  | Path to `id_ed25519.pub`  |
| --- | --- |
| macOS  | `~/.ollama/id_ed25519.pub`  |
| Linux  | `/usr/share/ollama/.ollama/id_ed25519.pub`  |
| Windows  | `C:\Users\<username>\.ollama\id_ed25519.pub`  |
Replace <username> with your actual Windows user name.
##
[​](https://docs.ollama.com/faq#how-can-i-stop-ollama-from-starting-when-i-login-to-my-computer)
How can I stop Ollama from starting when I login to my computer?
Ollama for Windows and macOS register as a login item during installation. You can disable this if you prefer not to have Ollama automatically start. Ollama will respect this setting across upgrades, unless you uninstall the application. **Windows**
  * In `Task Manager` go to the `Startup apps` tab, search for `ollama` then click `Disable`

**MacOS**
  * Open `Settings` and search for “Login Items”, find the `Ollama` entry under `Allow in the Background`, then click the slider to disable.


[Previous](https://docs.ollama.com/import)[ Hardware support Next ](https://docs.ollama.com/gpu)
⌘I
On this page
  * [How can I upgrade Ollama?](https://docs.ollama.com/faq#how-can-i-upgrade-ollama)
  * [How can I view the logs?](https://docs.ollama.com/faq#how-can-i-view-the-logs)
  * [Is my GPU compatible with Ollama?](https://docs.ollama.com/faq#is-my-gpu-compatible-with-ollama)
  * [How can I specify the context window size?](https://docs.ollama.com/faq#how-can-i-specify-the-context-window-size)
  * [How can I tell if my model was loaded onto the GPU?](https://docs.ollama.com/faq#how-can-i-tell-if-my-model-was-loaded-onto-the-gpu)
  * [How do I configure Ollama server?](https://docs.ollama.com/faq#how-do-i-configure-ollama-server)
  * [Setting environment variables on Mac](https://docs.ollama.com/faq#setting-environment-variables-on-mac)
  * [Setting environment variables on Linux](https://docs.ollama.com/faq#setting-environment-variables-on-linux)
  * [Setting environment variables on Windows](https://docs.ollama.com/faq#setting-environment-variables-on-windows)
  * [How do I use Ollama behind a proxy?](https://docs.ollama.com/faq#how-do-i-use-ollama-behind-a-proxy)
  * [How do I use Ollama behind a proxy in Docker?](https://docs.ollama.com/faq#how-do-i-use-ollama-behind-a-proxy-in-docker)
  * [Does Ollama send my prompts and answers back to ollama.com?](https://docs.ollama.com/faq#does-ollama-send-my-prompts-and-answers-back-to-ollama-com)
  * [How do I disable Ollama’s cloud features?](https://docs.ollama.com/faq#how-do-i-disable-ollama%E2%80%99s-cloud-features)
  * [How can I expose Ollama on my network?](https://docs.ollama.com/faq#how-can-i-expose-ollama-on-my-network)
  * [How can I use Ollama with a proxy server?](https://docs.ollama.com/faq#how-can-i-use-ollama-with-a-proxy-server)
  * [How can I use Ollama with ngrok?](https://docs.ollama.com/faq#how-can-i-use-ollama-with-ngrok)
  * [How can I use Ollama with Cloudflare Tunnel?](https://docs.ollama.com/faq#how-can-i-use-ollama-with-cloudflare-tunnel)
  * [How can I allow additional web origins to access Ollama?](https://docs.ollama.com/faq#how-can-i-allow-additional-web-origins-to-access-ollama)
  * [Where are models stored?](https://docs.ollama.com/faq#where-are-models-stored)
  * [How do I set them to a different location?](https://docs.ollama.com/faq#how-do-i-set-them-to-a-different-location)
  * [How can I use Ollama in Visual Studio Code?](https://docs.ollama.com/faq#how-can-i-use-ollama-in-visual-studio-code)
  * [How do I use Ollama with GPU acceleration in Docker?](https://docs.ollama.com/faq#how-do-i-use-ollama-with-gpu-acceleration-in-docker)
  * [Why is networking slow in WSL2 on Windows 10?](https://docs.ollama.com/faq#why-is-networking-slow-in-wsl2-on-windows-10)
  * [How can I preload a model into Ollama to get faster response times?](https://docs.ollama.com/faq#how-can-i-preload-a-model-into-ollama-to-get-faster-response-times)
  * [How do I keep a model loaded in memory or make it unload immediately?](https://docs.ollama.com/faq#how-do-i-keep-a-model-loaded-in-memory-or-make-it-unload-immediately)
  * [How do I manage the maximum number of requests the Ollama server can queue?](https://docs.ollama.com/faq#how-do-i-manage-the-maximum-number-of-requests-the-ollama-server-can-queue)
  * [How does Ollama handle concurrent requests?](https://docs.ollama.com/faq#how-does-ollama-handle-concurrent-requests)
  * [How does Ollama load models on multiple GPUs?](https://docs.ollama.com/faq#how-does-ollama-load-models-on-multiple-gpus)
  * [How can I enable Flash Attention?](https://docs.ollama.com/faq#how-can-i-enable-flash-attention)
  * [How can I set the quantization type for the K/V cache?](https://docs.ollama.com/faq#how-can-i-set-the-quantization-type-for-the-k%2Fv-cache)
  * [Where can I find my Ollama Public Key?](https://docs.ollama.com/faq#where-can-i-find-my-ollama-public-key)
  * [How to Add the Key](https://docs.ollama.com/faq#how-to-add-the-key)
  * [Where the Ollama Public Key lives](https://docs.ollama.com/faq#where-the-ollama-public-key-lives)
  * [How can I stop Ollama from starting when I login to my computer?](https://docs.ollama.com/faq#how-can-i-stop-ollama-from-starting-when-i-login-to-my-computer)


--- DOCUMENT: https://docs.ollama.com/gpu ---
# Hardware support
Copy page
Copy page
##
[​](https://docs.ollama.com/gpu#nvidia)
Nvidia
Ollama supports Nvidia GPUs with compute capability 5.0+ and driver version 531 and newer. Check your compute compatibility to see if your card is supported: <https://developer.nvidia.com/cuda-gpus>
| Compute Capability  | Family  | Cards  |
| --- | --- | --- |
| 12.1  | NVIDIA  | `GB10 (DGX Spark)`  |
| 12.0  | GeForce RTX 50xx  |  `RTX 5060` `RTX 5060 Ti` `RTX 5070` `RTX 5070 Ti` `RTX 5080` `RTX 5090`  |
|   | NVIDIA Professional  |  `RTX PRO 4000 Blackwell` `RTX PRO 4500 Blackwell` `RTX PRO 5000 Blackwell` `RTX PRO 6000 Blackwell`  |
| 9.0  | NVIDIA  |  `H200` `H100`  |
| 8.9  | GeForce RTX 40xx  |  `RTX 4090` `RTX 4080 SUPER` `RTX 4080` `RTX 4070 Ti SUPER` `RTX 4070 Ti` `RTX 4070 SUPER` `RTX 4070` `RTX 4060 Ti` `RTX 4060`  |
|   | NVIDIA Professional  |  `L4` `L40` `RTX 6000`  |
| 8.6  | GeForce RTX 30xx  |  `RTX 3090 Ti` `RTX 3090` `RTX 3080 Ti` `RTX 3080` `RTX 3070 Ti` `RTX 3070` `RTX 3060 Ti` `RTX 3060` `RTX 3050 Ti` `RTX 3050`  |
|   | NVIDIA Professional  |  `A40` `RTX A6000` `RTX A5000` `RTX A4000` `RTX A3000` `RTX A2000` `A10` `A16` `A2`  |
| 8.0  | NVIDIA  |  `A100` `A30`  |
| 7.5  | GeForce GTX/RTX  |  `GTX 1650 Ti` `TITAN RTX` `RTX 2080 Ti` `RTX 2080` `RTX 2070` `RTX 2060`  |
|   | NVIDIA Professional  |  `T4` `RTX 5000` `RTX 4000` `RTX 3000` `T2000` `T1200` `T1000` `T600` `T500`  |
|   | Quadro  |  `RTX 8000` `RTX 6000` `RTX 5000` `RTX 4000`  |
| 7.0  | NVIDIA  |  `TITAN V` `V100` `Quadro GV100`  |
| 6.1  | NVIDIA TITAN  |  `TITAN Xp` `TITAN X`  |
|   | GeForce GTX  |  `GTX 1080 Ti` `GTX 1080` `GTX 1070 Ti` `GTX 1070` `GTX 1060` `GTX 1050 Ti` `GTX 1050`  |
|   | Quadro  |  `P6000` `P5200` `P4200` `P3200` `P5000` `P4000` `P3000` `P2200` `P2000` `P1000` `P620` `P600` `P500` `P520`  |
|   | Tesla  |  `P40` `P4`  |
| 6.0  | NVIDIA  |  `Tesla P100` `Quadro GP100`  |
| 5.2  | GeForce GTX  |  `GTX TITAN X` `GTX 980 Ti` `GTX 980` `GTX 970` `GTX 960` `GTX 950`  |
|   | Quadro  |  `M6000 24GB` `M6000` `M5000` `M5500M` `M4000` `M2200` `M2000` `M620`  |
|   | Tesla  |  `M60` `M40`  |
| 5.0  | GeForce GTX  |  `GTX 750 Ti` `GTX 750` `NVS 810`  |
|   | Quadro  |  `K2200` `K1200` `K620` `M1200` `M520` `M5000M` `M4000M` `M3000M` `M2000M` `M1000M` `K620M` `M600M` `M500M`  |
For building locally to support older GPUs, see [developer](https://docs.ollama.com/development#linux-cuda-nvidia)
###
[​](https://docs.ollama.com/gpu#gpu-selection)
GPU Selection
If you have multiple NVIDIA GPUs in your system and want to limit Ollama to use a subset, you can set `CUDA_VISIBLE_DEVICES` to a comma separated list of GPUs. Numeric IDs may be used, however ordering may vary, so UUIDs are more reliable. You can discover the UUID of your GPUs by running `nvidia-smi -L` If you want to ignore the GPUs and force CPU usage, use an invalid GPU ID (e.g., “-1”)
###
[​](https://docs.ollama.com/gpu#linux-suspend-resume)
Linux Suspend Resume
On linux, after a suspend/resume cycle, sometimes Ollama will fail to discover your NVIDIA GPU, and fallback to running on the CPU. You can workaround this driver bug by reloading the NVIDIA UVM driver with `sudo rmmod nvidia_uvm && sudo modprobe nvidia_uvm`
##
[​](https://docs.ollama.com/gpu#amd-radeon)
AMD Radeon
Ollama supports the following AMD GPUs via the ROCm library:
> **NOTE:** Additional AMD GPU support is provided by the Vulkan Library - see below.
###
[​](https://docs.ollama.com/gpu#linux-support)
Linux Support
Ollama requires the AMD ROCm v7 driver on Linux. You can install or upgrade using the `amdgpu-install` utility from [AMD’s ROCm documentation](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/).
| Family  | Cards and accelerators  |
| --- | --- |
| AMD Radeon RX  |  `9070 XT` `9070 GRE` `9070` `9060 XT` `9060 XT LP` `9060` `7900 XTX` `7900 XT` `7900 GRE` `7800 XT` `7700 XT` `7700` `7600 XT` `7600` `6950 XT` `6900 XTX` `6900XT` `6800 XT` `6800` `5700 XT` `5700` `5600 XT` `5500 XT`  |
| AMD Radeon AI PRO  |  `R9700` `R9600D`  |
| AMD Radeon PRO  |  `W7900` `W7800` `W7700` `W7600` `W7500` `W6900X` `W6800X Duo` `W6800X` `W6800` `V620`  |
| AMD Ryzen AI  |  `Ryzen AI Max+ 395` `Ryzen AI Max 390` `Ryzen AI Max 385` `Ryzen AI 9 HX 475` `Ryzen AI 9 HX 470` `Ryzen AI 9 465` `Ryzen AI 9 HX 375` `Ryzen AI 9 HX 370` `Ryzen AI 9 365`  |
| AMD Instinct  |  `MI350X` `MI300X` `MI300A` `MI250X` `MI250` `MI210` `MI100`  |
###
[​](https://docs.ollama.com/gpu#windows-support)
Windows Support
With ROCm v6.1, the following GPUs are supported on Windows.
| Family  | Cards and accelerators  |
| --- | --- |
| AMD Radeon RX  |  `7900 XTX` `7900 XT` `7900 GRE` `7800 XT` `7700 XT` `7600 XT` `7600` `6950 XT` `6900 XTX` `6900XT` `6800 XT` `6800`  |
| AMD Radeon PRO  |  `W7900` `W7800` `W7700` `W7600` `W7500` `W6900X` `W6800X Duo` `W6800X` `W6800` `V620`  |
###
[​](https://docs.ollama.com/gpu#overrides-on-linux)
Overrides on Linux
Ollama leverages the AMD ROCm library, which does not support all AMD GPUs. In some cases you can force the system to try to use a similar LLVM target that is close. For example The Radeon RX 5400 is `gfx1034` (also known as 10.3.4) however, ROCm does not currently support this target. The closest support is `gfx1030`. You can use the environment variable `HSA_OVERRIDE_GFX_VERSION` with `x.y.z` syntax. So for example, to force the system to run on the RX 5400, you would set `HSA_OVERRIDE_GFX_VERSION="10.3.0"` as an environment variable for the server. If you have an unsupported AMD GPU you can experiment using the list of supported types below. If you have multiple GPUs with different GFX versions, append the numeric device number to the environment variable to set them individually. For example, `HSA_OVERRIDE_GFX_VERSION_0=10.3.0` and `HSA_OVERRIDE_GFX_VERSION_1=11.0.0` At this time, the known supported GPU types on linux are the following LLVM Targets. This table shows some example GPUs that map to these LLVM targets:
| **LLVM Target**  | **An Example GPU**  |
| --- | --- |
| gfx908  | Radeon Instinct MI100  |
| gfx90a  | Radeon Instinct MI210/MI250  |
| gfx942  | Radeon Instinct MI300X/MI300A  |
| gfx950  | Radeon Instinct MI350X  |
| gfx1010  | Radeon RX 5700 XT  |
| gfx1012  | Radeon RX 5500 XT  |
| gfx1030  | Radeon PRO V620  |
| gfx1100  | Radeon PRO W7900  |
| gfx1101  | Radeon PRO W7700  |
| gfx1102  | Radeon RX 7600  |
| gfx1103  | Radeon 780M  |
| gfx1150  | Ryzen AI 9 HX 375  |
| gfx1151  | Ryzen AI Max+ 395  |
| gfx1200  | Radeon RX 9070  |
| gfx1201  | Radeon RX 9070 XT  |
Reach out on [Discord](https://discord.gg/ollama) or file an [issue](https://github.com/ollama/ollama/issues) for additional help.
###
[​](https://docs.ollama.com/gpu#gpu-selection-2)
GPU Selection
If you have multiple AMD GPUs in your system and want to limit Ollama to use a subset, you can set `ROCR_VISIBLE_DEVICES` to a comma separated list of GPUs. You can see the list of devices with `rocminfo`. If you want to ignore the GPUs and force CPU usage, use an invalid GPU ID (e.g., “-1”). When available, use the `Uuid` to uniquely identify the device instead of numeric value.
###
[​](https://docs.ollama.com/gpu#container-permission)
Container Permission
In some Linux distributions, SELinux can prevent containers from accessing the AMD GPU devices. On the host system you can run `sudo setsebool container_use_devices=1` to allow containers to use devices.
##
[​](https://docs.ollama.com/gpu#metal-apple-gpus)
Metal (Apple GPUs)
Ollama supports GPU acceleration on Apple devices via the Metal API.
##
[​](https://docs.ollama.com/gpu#vulkan-gpu-support)
Vulkan GPU Support
> **NOTE:** Vulkan is currently an Experimental feature. To enable, you must set OLLAMA_VULKAN=1 for the Ollama server as described in the [FAQ](https://docs.ollama.com/faq#how-do-i-configure-ollama-server)
Additional GPU support on Windows and Linux is provided via [Vulkan](https://www.vulkan.org/). On Windows most GPU vendors drivers come bundled with Vulkan support and require no additional setup steps. Most Linux distributions require installing additional components, and you may have multiple options for Vulkan drivers between Mesa and GPU Vendor specific packages
  * Linux Intel GPU Instructions - <https://dgpu-docs.intel.com/driver/client/overview.html>
  * Linux AMD GPU Instructions - <https://amdgpu-install.readthedocs.io/en/latest/install-script.html#specifying-a-vulkan-implementation>

For AMD GPUs on some Linux distributions, you may need to add the `ollama` user to the `render` group. The Ollama scheduler leverages available VRAM data reported by the GPU libraries to make optimal scheduling decisions. Vulkan requires additional capabilities or running as root to expose this available VRAM data. If neither root access or this capability are granted, Ollama will use approximate sizes of the models to make best effort scheduling decisions.

```
sudo setcap cap_perfmon+ep /usr/local/bin/ollama

```

###
[​](https://docs.ollama.com/gpu#gpu-selection-3)
GPU Selection
To select specific Vulkan GPU(s), you can set the environment variable `GGML_VK_VISIBLE_DEVICES` to one or more numeric IDs on the Ollama server as described in the [FAQ](https://docs.ollama.com/faq#how-do-i-configure-ollama-server). If you encounter any problems with Vulkan based GPUs, you can disable all Vulkan GPUs by setting `GGML_VK_VISIBLE_DEVICES=-1`
[Previous](https://docs.ollama.com/faq)[ TroubleshootingHow to troubleshoot issues encountered with Ollama Next ](https://docs.ollama.com/troubleshooting)
⌘I
On this page
  * [Nvidia](https://docs.ollama.com/gpu#nvidia)
  * [GPU Selection](https://docs.ollama.com/gpu#gpu-selection)
  * [Linux Suspend Resume](https://docs.ollama.com/gpu#linux-suspend-resume)
  * [AMD Radeon](https://docs.ollama.com/gpu#amd-radeon)
  * [Linux Support](https://docs.ollama.com/gpu#linux-support)
  * [Windows Support](https://docs.ollama.com/gpu#windows-support)
  * [Overrides on Linux](https://docs.ollama.com/gpu#overrides-on-linux)
  * [GPU Selection](https://docs.ollama.com/gpu#gpu-selection-2)
  * [Container Permission](https://docs.ollama.com/gpu#container-permission)
  * [Metal (Apple GPUs)](https://docs.ollama.com/gpu#metal-apple-gpus)
  * [Vulkan GPU Support](https://docs.ollama.com/gpu#vulkan-gpu-support)
  * [GPU Selection](https://docs.ollama.com/gpu#gpu-selection-3)


--- DOCUMENT: https://docs.ollama.com/import ---
# Importing a Model
Copy page
Copy page
##
[​](https://docs.ollama.com/import#table-of-contents)
Table of Contents
  * [Importing a Safetensors adapter](https://docs.ollama.com/import#Importing-a-fine-tuned-adapter-from-Safetensors-weights)
  * [Importing a Safetensors model](https://docs.ollama.com/import#Importing-a-model-from-Safetensors-weights)
  * [Importing a GGUF file](https://docs.ollama.com/import#Importing-a-GGUF-based-model-or-adapter)
  * [Sharing models on ollama.com](https://docs.ollama.com/import#Sharing-your-model-on-ollamacom)


##
[​](https://docs.ollama.com/import#importing-a-fine-tuned-adapter-from-safetensors-weights)
Importing a fine tuned adapter from Safetensors weights
First, create a `Modelfile` with a `FROM` command pointing at the base model you used for fine tuning, and an `ADAPTER` command which points to the directory with your Safetensors adapter:

```
FROM <base model name>
ADAPTER /path/to/safetensors/adapter/directory

```

Make sure that you use the same base model in the `FROM` command as you used to create the adapter otherwise you will get erratic results. Most frameworks use different quantization methods, so it’s best to use non-quantized (i.e. non-QLoRA) adapters. If your adapter is in the same directory as your `Modelfile`, use `ADAPTER .` to specify the adapter path. Now run `ollama create` from the directory where the `Modelfile` was created:

```
ollama create my-model

```

Lastly, test the model:

```
ollama run my-model

```

Ollama supports importing adapters based on several different model architectures including:
  * Llama (including Llama 2, Llama 3, Llama 3.1, and Llama 3.2);
  * Mistral (including Mistral 1, Mistral 2, and Mixtral); and
  * Gemma (including Gemma 1 and Gemma 2)

You can create the adapter using a fine tuning framework or tool which can output adapters in the Safetensors format, such as:
  * Hugging Face [fine tuning framework](https://huggingface.co/docs/transformers/en/training)
  * [Unsloth](https://github.com/unslothai/unsloth)
  * [MLX](https://github.com/ml-explore/mlx)


##
[​](https://docs.ollama.com/import#importing-a-model-from-safetensors-weights)
Importing a model from Safetensors weights
First, create a `Modelfile` with a `FROM` command which points to the directory containing your Safetensors weights:

```
FROM /path/to/safetensors/directory

```

If you create the Modelfile in the same directory as the weights, you can use the command `FROM .`. Now run the `ollama create` command from the directory where you created the `Modelfile`:

```
ollama create my-model

```

Lastly, test the model:

```
ollama run my-model

```

Ollama supports importing models for several different architectures including:
  * Llama (including Llama 2, Llama 3, Llama 3.1, and Llama 3.2);
  * Mistral (including Mistral 1, Mistral 2, and Mixtral);
  * Gemma (including Gemma 1 and Gemma 2); and
  * Phi3

This includes importing foundation models as well as any fine tuned models which have been _fused_ with a foundation model.
##
[​](https://docs.ollama.com/import#importing-a-gguf-based-model-or-adapter)
Importing a GGUF based model or adapter
If you have a GGUF based model or adapter it is possible to import it into Ollama. You can obtain a GGUF model or adapter by:
  * converting a Safetensors model with the `convert_hf_to_gguf.py` from Llama.cpp;
  * converting a Safetensors adapter with the `convert_lora_to_gguf.py` from Llama.cpp; or
  * downloading a model or adapter from a place such as HuggingFace

To import a GGUF model, create a `Modelfile` containing:

```
FROM /path/to/file.gguf

```

For a GGUF adapter, create the `Modelfile` with:

```
FROM <model name>
ADAPTER /path/to/file.gguf

```

When importing a GGUF adapter, it’s important to use the same base model as the base model that the adapter was created with. You can use:
  * a model from Ollama
  * a GGUF file
  * a Safetensors based model

Once you have created your `Modelfile`, use the `ollama create` command to build the model.

```
ollama create my-model

```

##
[​](https://docs.ollama.com/import#quantizing-a-model)
Quantizing a Model
Quantizing a model allows you to run models faster and with less memory consumption but at reduced accuracy. This allows you to run a model on more modest hardware. Ollama can quantize FP16 and FP32 based models into different quantization levels using the `-q/--quantize` flag with the `ollama create` command. First, create a Modelfile with the FP16 or FP32 based model you wish to quantize.

```
FROM /path/to/my/gemma/f16/model

```

Use `ollama create` to then create the quantized model.

```
$ ollama create --quantize q4_K_M mymodel
transferring model data
quantizing F16 model to Q4_K_M
creating new layer sha256:735e246cc1abfd06e9cdcf95504d6789a6cd1ad7577108a70d9902fef503c1bd
creating new layer sha256:0853f0ad24e5865173bbf9ffcc7b0f5d56b66fd690ab1009867e45e7d2c4db0f
writing manifest
success

```

###
[​](https://docs.ollama.com/import#supported-quantizations)
Supported Quantizations
  * `q8_0`


####
[​](https://docs.ollama.com/import#k-means-quantizations)
K-means Quantizations
  * `q4_K_S`
  * `q4_K_M`


##
[​](https://docs.ollama.com/import#sharing-your-model-on-ollama-com)
Sharing your model on ollama.com
You can share any model you have created by pushing it to [ollama.com](https://ollama.com) so that other users can try it out. First, use your browser to go to the [Ollama Sign-Up](https://ollama.com/signup) page. If you already have an account, you can skip this step. ![Sign-Up](https://mintcdn.com/ollama-9269c548/uieua2DvLKVQ74Ga/images/signup.png?fit=max&auto=format&n=uieua2DvLKVQ74Ga&q=85&s=d99f1340e6cfd85d36d49a444491cc63) The `Username` field will be used as part of your model’s name (e.g. `jmorganca/mymodel`), so make sure you are comfortable with the username that you have selected. Now that you have created an account and are signed-in, go to the [Ollama Keys Settings](https://ollama.com/settings/keys) page. Follow the directions on the page to determine where your Ollama Public Key is located. ![Ollama Keys](https://mintcdn.com/ollama-9269c548/uieua2DvLKVQ74Ga/images/ollama-keys.png?fit=max&auto=format&n=uieua2DvLKVQ74Ga&q=85&s=7ced4d97ecf6b115219f929a4914205e) Click on the `Add Ollama Public Key` button, and copy and paste the contents of your Ollama Public Key into the text field. To push a model to [ollama.com](https://ollama.com), first make sure that it is named correctly with your username. You may have to use the `ollama cp` command to copy your model to give it the correct name. Once you’re happy with your model’s name, use the `ollama push` command to push it to [ollama.com](https://ollama.com).

```
ollama cp mymodel myuser/mymodel
ollama push myuser/mymodel

```

Once your model has been pushed, other users can pull and run it by using the command:

```
ollama run myuser/mymodel

```

[Previous](https://docs.ollama.com/docker)[ FAQ Next ](https://docs.ollama.com/faq)
⌘I
On this page
  * [Table of Contents](https://docs.ollama.com/import#table-of-contents)
  * [Importing a fine tuned adapter from Safetensors weights](https://docs.ollama.com/import#importing-a-fine-tuned-adapter-from-safetensors-weights)
  * [Importing a model from Safetensors weights](https://docs.ollama.com/import#importing-a-model-from-safetensors-weights)
  * [Importing a GGUF based model or adapter](https://docs.ollama.com/import#importing-a-gguf-based-model-or-adapter)
  * [Quantizing a Model](https://docs.ollama.com/import#quantizing-a-model)
  * [Supported Quantizations](https://docs.ollama.com/import#supported-quantizations)
  * [K-means Quantizations](https://docs.ollama.com/import#k-means-quantizations)
  * [Sharing your model on ollama.com](https://docs.ollama.com/import#sharing-your-model-on-ollama-com)


--- DOCUMENT: https://docs.ollama.com/integrations ---
# Overview
Copy page
Copy page
Ollama integrates with a wide range of tools.
##
[​](https://docs.ollama.com/integrations#coding-agents)
Coding Agents
Coding assistants that can read, modify, and execute code in your projects.
  * [Claude Code](https://docs.ollama.com/integrations/claude-code)
  * [Codex](https://docs.ollama.com/integrations/codex)
  * [Copilot CLI](https://docs.ollama.com/integrations/copilot-cli)
  * [OpenCode](https://docs.ollama.com/integrations/opencode)
  * [Droid](https://docs.ollama.com/integrations/droid)
  * [Goose](https://docs.ollama.com/integrations/goose)
  * [Pi](https://docs.ollama.com/integrations/pi)


##
[​](https://docs.ollama.com/integrations#assistants)
Assistants
AI assistants that help with everyday tasks.
  * [OpenClaw](https://docs.ollama.com/integrations/openclaw)
  * [Hermes Agent](https://docs.ollama.com/integrations/hermes)


##
[​](https://docs.ollama.com/integrations#ides-&-editors)
IDEs & Editors
Native integrations for popular development environments.
  * [VS Code](https://docs.ollama.com/integrations/vscode)
  * [Cline](https://docs.ollama.com/integrations/cline)
  * [Roo Code](https://docs.ollama.com/integrations/roo-code)
  * [JetBrains](https://docs.ollama.com/integrations/jetbrains)
  * [Xcode](https://docs.ollama.com/integrations/xcode)
  * [Zed](https://docs.ollama.com/integrations/zed)


##
[​](https://docs.ollama.com/integrations#chat-&-rag)
Chat & RAG
Chat interfaces and retrieval-augmented generation platforms.
  * [Onyx](https://docs.ollama.com/integrations/onyx)


##
[​](https://docs.ollama.com/integrations#automation)
Automation
Workflow automation platforms with AI integration.
  * [n8n](https://docs.ollama.com/integrations/n8n)


##
[​](https://docs.ollama.com/integrations#notebooks)
Notebooks
Interactive computing environments with AI capabilities.
  * [marimo](https://docs.ollama.com/integrations/marimo)


[Previous](https://docs.ollama.com/capabilities/web-search)[ OpenClaw Next ](https://docs.ollama.com/integrations/openclaw)
⌘I
On this page
  * [Coding Agents](https://docs.ollama.com/integrations#coding-agents)
  * [Assistants](https://docs.ollama.com/integrations#assistants)
  * [IDEs & Editors](https://docs.ollama.com/integrations#ides-%26-editors)
  * [Chat & RAG](https://docs.ollama.com/integrations#chat-%26-rag)
  * [Automation](https://docs.ollama.com/integrations#automation)
  * [Notebooks](https://docs.ollama.com/integrations#notebooks)


--- DOCUMENT: https://docs.ollama.com/linux ---
# Linux
Copy page
Copy page
##
[​](https://docs.ollama.com/linux#install)
Install
To install Ollama, run the following command:

```
curl -fsSL https://ollama.com/install.sh | sh

```

##
[​](https://docs.ollama.com/linux#manual-install)
Manual install
If you are upgrading from a prior version, you should remove the old libraries with `sudo rm -rf /usr/lib/ollama` first.
Download and extract the package:

```
curl -fsSL https://ollama.com/download/ollama-linux-amd64.tar.zst \
    | sudo tar x -C /usr

```

Start Ollama:

```
ollama serve

```

In another terminal, verify that Ollama is running:

```
ollama -v

```

###
[​](https://docs.ollama.com/linux#amd-gpu-install)
AMD GPU install
If you have an AMD GPU, also download and extract the additional ROCm package:

```
curl -fsSL https://ollama.com/download/ollama-linux-amd64-rocm.tar.zst \
    | sudo tar x -C /usr

```

###
[​](https://docs.ollama.com/linux#arm64-install)
ARM64 install
Download and extract the ARM64-specific package:

```
curl -fsSL https://ollama.com/download/ollama-linux-arm64.tar.zst \
    | sudo tar x -C /usr

```

###
[​](https://docs.ollama.com/linux#adding-ollama-as-a-startup-service-recommended)
Adding Ollama as a startup service (recommended)
Create a user and group for Ollama:

```
sudo useradd -r -s /bin/false -U -m -d /usr/share/ollama ollama
sudo usermod -a -G ollama $(whoami)

```

Create a service file in `/etc/systemd/system/ollama.service`:

```
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="PATH=$PATH"

[Install]
WantedBy=multi-user.target

```

Then start the service:

```
sudo systemctl daemon-reload
sudo systemctl enable ollama

```

###
[​](https://docs.ollama.com/linux#install-cuda-drivers-optional)
Install CUDA drivers (optional)
[Download and install](https://developer.nvidia.com/cuda-downloads) CUDA. Verify that the drivers are installed by running the following command, which should print details about your GPU:

```
nvidia-smi

```

###
[​](https://docs.ollama.com/linux#install-amd-rocm-drivers-optional)
Install AMD ROCm drivers (optional)
[Download and Install](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/tutorial/quick-start.html) ROCm v7.
###
[​](https://docs.ollama.com/linux#start-ollama)
Start Ollama
Start Ollama and verify it is running:

```
sudo systemctl start ollama
sudo systemctl status ollama

```

While AMD has contributed the `amdgpu` driver upstream to the official linux kernel source, the version is older and may not support all ROCm features. We recommend you install the latest driver from <https://www.amd.com/en/support/linux-drivers> for best support of your Radeon GPU.
##
[​](https://docs.ollama.com/linux#customizing)
Customizing
To customize the installation of Ollama, you can edit the systemd service file or the environment variables by running:

```
sudo systemctl edit ollama

```

Alternatively, create an override file manually in `/etc/systemd/system/ollama.service.d/override.conf`:

```
[Service]
Environment="OLLAMA_DEBUG=1"

```

##
[​](https://docs.ollama.com/linux#updating)
Updating
Update Ollama by running the install script again:

```
curl -fsSL https://ollama.com/install.sh | sh

```

Or by re-downloading Ollama:

```
curl -fsSL https://ollama.com/download/ollama-linux-amd64.tar.zst \
    | sudo tar x -C /usr

```

##
[​](https://docs.ollama.com/linux#installing-specific-versions)
Installing specific versions
Use `OLLAMA_VERSION` environment variable with the install script to install a specific version of Ollama, including pre-releases. You can find the version numbers in the [releases page](https://github.com/ollama/ollama/releases). For example:

```
curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.5.7 sh

```

##
[​](https://docs.ollama.com/linux#viewing-logs)
Viewing logs
To view logs of Ollama running as a startup service, run:

```
journalctl -e -u ollama

```

##
[​](https://docs.ollama.com/linux#uninstall)
Uninstall
Remove the ollama service:

```
sudo systemctl stop ollama
sudo systemctl disable ollama
sudo rm /etc/systemd/system/ollama.service

```

Remove ollama libraries from your lib directory (either `/usr/local/lib`, `/usr/lib`, or `/lib`):

```
sudo rm -r $(which ollama | tr 'bin' 'lib')

```

Remove the ollama binary from your bin directory (either `/usr/local/bin`, `/usr/bin`, or `/bin`):

```
sudo rm $(which ollama)

```

Remove the downloaded models and Ollama service user and group:

```
sudo userdel ollama
sudo groupdel ollama
sudo rm -r /usr/share/ollama

```

[Previous](https://docs.ollama.com/context-length)[ macOS Next ](https://docs.ollama.com/macos)
⌘I
On this page
  * [Install](https://docs.ollama.com/linux#install)
  * [Manual install](https://docs.ollama.com/linux#manual-install)
  * [AMD GPU install](https://docs.ollama.com/linux#amd-gpu-install)
  * [ARM64 install](https://docs.ollama.com/linux#arm64-install)
  * [Adding Ollama as a startup service (recommended)](https://docs.ollama.com/linux#adding-ollama-as-a-startup-service-recommended)
  * [Install CUDA drivers (optional)](https://docs.ollama.com/linux#install-cuda-drivers-optional)
  * [Install AMD ROCm drivers (optional)](https://docs.ollama.com/linux#install-amd-rocm-drivers-optional)
  * [Start Ollama](https://docs.ollama.com/linux#start-ollama)
  * [Customizing](https://docs.ollama.com/linux#customizing)
  * [Updating](https://docs.ollama.com/linux#updating)
  * [Installing specific versions](https://docs.ollama.com/linux#installing-specific-versions)
  * [Viewing logs](https://docs.ollama.com/linux#viewing-logs)
  * [Uninstall](https://docs.ollama.com/linux#uninstall)


--- DOCUMENT: https://docs.ollama.com/macos ---
# macOS
Copy page
Copy page
##
[​](https://docs.ollama.com/macos#system-requirements)
System Requirements
  * MacOS Sonoma (v14) or newer
  * Apple M series (CPU and GPU support) or x86 (CPU only)


##
[​](https://docs.ollama.com/macos#filesystem-requirements)
Filesystem Requirements
The preferred method of installation is to mount the `ollama.dmg` and drag-and-drop the Ollama application to the system-wide `Applications` folder. Upon startup, the Ollama app will verify the `ollama` CLI is present in your PATH, and if not detected, will prompt for permission to create a link in `/usr/local/bin` Once you’ve installed Ollama, you’ll need additional space for storing the Large Language models, which can be tens to hundreds of GB in size. If your home directory doesn’t have enough space, you can change where the binaries are installed, and where the models are stored.
###
[​](https://docs.ollama.com/macos#changing-install-location)
Changing Install Location
To install the Ollama application somewhere other than `Applications`, place the Ollama application in the desired location, and ensure the CLI `Ollama.app/Contents/Resources/ollama` or a sym-link to the CLI can be found in your path. Upon first start decline the “Move to Applications?” request.
##
[​](https://docs.ollama.com/macos#troubleshooting)
Troubleshooting
Ollama on MacOS stores files in a few different locations.
  * `~/.ollama` contains models and configuration
  * `~/.ollama/logs` contains logs
    * _app.log_ contains most recent logs from the GUI application
    * _server.log_ contains the most recent server logs
  * `<install location>/Ollama.app/Contents/Resources/ollama` the CLI binary


##
[​](https://docs.ollama.com/macos#uninstall)
Uninstall
To fully remove Ollama from your system, remove the following files and folders:

```
sudo rm -rf /Applications/Ollama.app
sudo rm /usr/local/bin/ollama
rm -rf "~/Library/Application Support/Ollama"
rm -rf "~/Library/Saved Application State/com.electron.ollama.savedState"
rm -rf ~/Library/Caches/com.electron.ollama/
rm -rf ~/Library/Caches/ollama
rm -rf ~/Library/WebKit/com.electron.ollama
rm -rf ~/.ollama

```

[Previous](https://docs.ollama.com/linux)[ Windows Next ](https://docs.ollama.com/windows)
⌘I
On this page
  * [System Requirements](https://docs.ollama.com/macos#system-requirements)
  * [Filesystem Requirements](https://docs.ollama.com/macos#filesystem-requirements)
  * [Changing Install Location](https://docs.ollama.com/macos#changing-install-location)
  * [Troubleshooting](https://docs.ollama.com/macos#troubleshooting)
  * [Uninstall](https://docs.ollama.com/macos#uninstall)


--- DOCUMENT: https://docs.ollama.com/modelfile ---
# Modelfile Reference
Copy page
Copy page
A Modelfile is the blueprint to create and share customized models using Ollama.
##
[​](https://docs.ollama.com/modelfile#table-of-contents)
Table of Contents
  * [Format](https://docs.ollama.com/modelfile#format)
  * [Examples](https://docs.ollama.com/modelfile#examples)
  * [Instructions](https://docs.ollama.com/modelfile#instructions)
    * [FROM (Required)](https://docs.ollama.com/modelfile#from-required)
      * [Build from existing model](https://docs.ollama.com/modelfile#build-from-existing-model)
      * [Build from a Safetensors model](https://docs.ollama.com/modelfile#build-from-a-safetensors-model)
      * [Build from a GGUF file](https://docs.ollama.com/modelfile#build-from-a-gguf-file)
    * [PARAMETER](https://docs.ollama.com/modelfile#parameter)
      * [Valid Parameters and Values](https://docs.ollama.com/modelfile#valid-parameters-and-values)
    * [TEMPLATE](https://docs.ollama.com/modelfile#template)
      * [Template Variables](https://docs.ollama.com/modelfile#template-variables)
    * [SYSTEM](https://docs.ollama.com/modelfile#system)
    * [ADAPTER](https://docs.ollama.com/modelfile#adapter)
    * [LICENSE](https://docs.ollama.com/modelfile#license)
    * [MESSAGE](https://docs.ollama.com/modelfile#message)
  * [Notes](https://docs.ollama.com/modelfile#notes)


##
[​](https://docs.ollama.com/modelfile#format)
Format
The format of the `Modelfile`:

```
# comment
INSTRUCTION arguments

```

| Instruction  | Description  |
| --- | --- |
|  [`FROM`](https://docs.ollama.com/modelfile#from-required) (required)  | Defines the base model to use.  |
| [`PARAMETER`](https://docs.ollama.com/modelfile#parameter)  | Sets the parameters for how Ollama will run the model.  |
| [`TEMPLATE`](https://docs.ollama.com/modelfile#template)  | The full prompt template to be sent to the model.  |
| [`SYSTEM`](https://docs.ollama.com/modelfile#system)  | Specifies the system message that will be set in the template.  |
| [`ADAPTER`](https://docs.ollama.com/modelfile#adapter)  | Defines the (Q)LoRA adapters to apply to the model.  |
| [`LICENSE`](https://docs.ollama.com/modelfile#license)  | Specifies the legal license.  |
| [`MESSAGE`](https://docs.ollama.com/modelfile#message)  | Specify message history.  |
| [`REQUIRES`](https://docs.ollama.com/modelfile#requires)  | Specify the minimum version of Ollama required by the model.  |
##
[​](https://docs.ollama.com/modelfile#examples)
Examples
###
[​](https://docs.ollama.com/modelfile#basic-modelfile)
Basic `Modelfile`
An example of a `Modelfile` creating a mario blueprint:

```
FROM llama3.2
# sets the temperature to 1 [higher is more creative, lower is more coherent]
PARAMETER temperature 1
# sets the context window size to 4096, this controls how many tokens the LLM can use as context to generate the next token
PARAMETER num_ctx 4096

# sets a custom system message to specify the behavior of the chat assistant
SYSTEM You are Mario from super mario bros, acting as an assistant.

```

To use this:
  1. Save it as a file (e.g. `Modelfile`)
  2. `ollama create choose-a-model-name -f <location of the file e.g. ./Modelfile>`
  3. `ollama run choose-a-model-name`
  4. Start using the model!

To view the Modelfile of a given model, use the `ollama show --modelfile` command.

```
ollama show --modelfile llama3.2

```


```
# Modelfile generated by "ollama show"
# To build a new Modelfile based on this one, replace the FROM line with:
# FROM llama3.2:latest
FROM /Users/pdevine/.ollama/models/blobs/sha256-00e1317cbf74d901080d7100f57580ba8dd8de57203072dc6f668324ba545f29
TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

{{ .Response }}<|eot_id|>"""
PARAMETER stop "<|start_header_id|>"
PARAMETER stop "<|end_header_id|>"
PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|reserved_special_token"

```

##
[​](https://docs.ollama.com/modelfile#instructions)
Instructions
###
[​](https://docs.ollama.com/modelfile#from-required)
FROM (Required)
The `FROM` instruction defines the base model to use when creating a model.

```
FROM <model name>:<tag>

```

####
[​](https://docs.ollama.com/modelfile#build-from-existing-model)
Build from existing model

```
FROM llama3.2

```

## Base Models
A list of available base models
## Base Models
Additional models can be found at
####
[​](https://docs.ollama.com/modelfile#build-from-a-safetensors-model)
Build from a Safetensors model

```
FROM <model directory>

```

The model directory should contain the Safetensors weights for a supported architecture. Currently supported model architectures:
  * Llama (including Llama 2, Llama 3, Llama 3.1, and Llama 3.2)
  * Mistral (including Mistral 1, Mistral 2, and Mixtral)
  * Gemma (including Gemma 1 and Gemma 2)
  * Phi3


####
[​](https://docs.ollama.com/modelfile#build-from-a-gguf-file)
Build from a GGUF file

```
FROM ./ollama-model.gguf

```

The GGUF file location should be specified as an absolute path or relative to the `Modelfile` location.
###
[​](https://docs.ollama.com/modelfile#parameter)
PARAMETER
The `PARAMETER` instruction defines a parameter that can be set when the model is run.

```
PARAMETER <parameter> <parametervalue>

```

####
[​](https://docs.ollama.com/modelfile#valid-parameters-and-values)
Valid Parameters and Values
| Parameter  | Description  | Value Type  | Example Usage  |
| --- | --- | --- | --- |
| num_ctx  | Sets the size of the context window used to generate the next token. (Default: 2048)  | int  | num_ctx 4096  |
| repeat_last_n  | Sets how far back for the model to look back to prevent repetition. (Default: 64, 0 = disabled, -1 = num_ctx)  | int  | repeat_last_n 64  |
| repeat_penalty  | Sets how strongly to penalize repetitions. A higher value (e.g., 1.5) will penalize repetitions more strongly, while a lower value (e.g., 0.9) will be more lenient. (Default: 1.1)  | float  | repeat_penalty 1.1  |
| temperature  | The temperature of the model. Increasing the temperature will make the model answer more creatively. (Default: 0.8)  | float  | temperature 0.7  |
| seed  | Sets the random number seed to use for generation. Setting this to a specific number will make the model generate the same text for the same prompt. (Default: 0)  | int  | seed 42  |
| stop  | Sets the stop sequences to use. When this pattern is encountered the LLM will stop generating text and return. Multiple stop patterns may be set by specifying multiple separate `stop` parameters in a modelfile.  | string  | stop “AI assistant:“  |
| num_predict  | Maximum number of tokens to predict when generating text. (Default: -1, infinite generation)  | int  | num_predict 42  |
| top_k  | Reduces the probability of generating nonsense. A higher value (e.g. 100) will give more diverse answers, while a lower value (e.g. 10) will be more conservative. (Default: 40)  | int  | top_k 40  |
| top_p  | Works together with top-k. A higher value (e.g., 0.95) will lead to more diverse text, while a lower value (e.g., 0.5) will generate more focused and conservative text. (Default: 0.9)  | float  | top_p 0.9  |
| min_p  | Alternative to the top _p, and aims to ensure a balance of quality and variety. The parameter _p_ represents the minimum probability for a token to be considered, relative to the probability of the most likely token. For example, with _p_ =0.05 and the most likely token having a probability of 0.9, logits with a value less than 0.045 are filtered out. (Default: 0.0)  | float  | min_p 0.05  |
###
[​](https://docs.ollama.com/modelfile#template)
TEMPLATE
`TEMPLATE` of the full prompt template to be passed into the model. It may include (optionally) a system message, a user’s message and the response from the model. Note: syntax may be model specific. Templates use Go [template syntax](https://pkg.go.dev/text/template).
####
[​](https://docs.ollama.com/modelfile#template-variables)
Template Variables
| Variable  | Description  |
| --- | --- |
| `{{ .System }}`  | The system message used to specify custom behavior.  |
| `{{ .Prompt }}`  | The user prompt message.  |
| `{{ .Response }}`  | The response from the model. When generating a response, text after this variable is omitted.  |

```
TEMPLATE """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
"""

```

###
[​](https://docs.ollama.com/modelfile#system)
SYSTEM
The `SYSTEM` instruction specifies the system message to be used in the template, if applicable.

```
SYSTEM """<system message>"""

```

###
[​](https://docs.ollama.com/modelfile#adapter)
ADAPTER
The `ADAPTER` instruction specifies a fine tuned LoRA adapter that should apply to the base model. The value of the adapter should be an absolute path or a path relative to the Modelfile. The base model should be specified with a `FROM` instruction. If the base model is not the same as the base model that the adapter was tuned from the behaviour will be erratic.
####
[​](https://docs.ollama.com/modelfile#safetensor-adapter)
Safetensor adapter

```
ADAPTER <path to safetensor adapter>

```

Currently supported Safetensor adapters:
  * Llama (including Llama 2, Llama 3, and Llama 3.1)
  * Mistral (including Mistral 1, Mistral 2, and Mixtral)
  * Gemma (including Gemma 1 and Gemma 2)


####
[​](https://docs.ollama.com/modelfile#gguf-adapter)
GGUF adapter

```
ADAPTER ./ollama-lora.gguf

```

###
[​](https://docs.ollama.com/modelfile#license)
LICENSE
The `LICENSE` instruction allows you to specify the legal license under which the model used with this Modelfile is shared or distributed.

```
LICENSE """
<license text>
"""

```

###
[​](https://docs.ollama.com/modelfile#message)
MESSAGE
The `MESSAGE` instruction allows you to specify a message history for the model to use when responding. Use multiple iterations of the MESSAGE command to build up a conversation which will guide the model to answer in a similar way.

```
MESSAGE <role> <message>

```

####
[​](https://docs.ollama.com/modelfile#valid-roles)
Valid roles
| Role  | Description  |
| --- | --- |
| system  | Alternate way of providing the SYSTEM message for the model.  |
| user  | An example message of what the user could have asked.  |
| assistant  | An example message of how the model should respond.  |
####
[​](https://docs.ollama.com/modelfile#example-conversation)
Example conversation

```
MESSAGE user Is Toronto in Canada?
MESSAGE assistant yes
MESSAGE user Is Sacramento in Canada?
MESSAGE assistant no
MESSAGE user Is Ontario in Canada?
MESSAGE assistant yes

```

###
[​](https://docs.ollama.com/modelfile#requires)
REQUIRES
The `REQUIRES` instruction allows you to specify the minimum version of Ollama required by the model.

```
REQUIRES <version>

```

The version should be a valid Ollama version (e.g. 0.14.0).
##
[​](https://docs.ollama.com/modelfile#notes)
Notes
  * the **`Modelfile`is not case sensitive**. In the examples, uppercase instructions are used to make it easier to distinguish it from arguments.
  * Instructions can be in any order. In the examples, the `FROM` instruction is first to keep it easily readable.


[Previous](https://docs.ollama.com/integrations/nemoclaw)[ Context length Next ](https://docs.ollama.com/context-length)
⌘I
On this page
  * [Table of Contents](https://docs.ollama.com/modelfile#table-of-contents)
  * [Format](https://docs.ollama.com/modelfile#format)
  * [Examples](https://docs.ollama.com/modelfile#examples)
  * [Basic Modelfile](https://docs.ollama.com/modelfile#basic-modelfile)
  * [Instructions](https://docs.ollama.com/modelfile#instructions)
  * [FROM (Required)](https://docs.ollama.com/modelfile#from-required)
  * [Build from existing model](https://docs.ollama.com/modelfile#build-from-existing-model)
  * [Build from a Safetensors model](https://docs.ollama.com/modelfile#build-from-a-safetensors-model)
  * [Build from a GGUF file](https://docs.ollama.com/modelfile#build-from-a-gguf-file)
  * [PARAMETER](https://docs.ollama.com/modelfile#parameter)
  * [Valid Parameters and Values](https://docs.ollama.com/modelfile#valid-parameters-and-values)
  * [TEMPLATE](https://docs.ollama.com/modelfile#template)
  * [Template Variables](https://docs.ollama.com/modelfile#template-variables)
  * [SYSTEM](https://docs.ollama.com/modelfile#system)
  * [ADAPTER](https://docs.ollama.com/modelfile#adapter)
  * [Safetensor adapter](https://docs.ollama.com/modelfile#safetensor-adapter)
  * [GGUF adapter](https://docs.ollama.com/modelfile#gguf-adapter)
  * [LICENSE](https://docs.ollama.com/modelfile#license)
  * [MESSAGE](https://docs.ollama.com/modelfile#message)
  * [Valid roles](https://docs.ollama.com/modelfile#valid-roles)
  * [Example conversation](https://docs.ollama.com/modelfile#example-conversation)
  * [REQUIRES](https://docs.ollama.com/modelfile#requires)
  * [Notes](https://docs.ollama.com/modelfile#notes)


--- DOCUMENT: https://docs.ollama.com/quickstart ---
# Quickstart
Copy page
Copy page
Ollama is available on macOS, Windows, and Linux. [Download Ollama](https://ollama.com/download)
##
[​](https://docs.ollama.com/quickstart#get-started)
Get Started
Run `ollama` in your terminal to open the interactive menu:

```
ollama

```

Navigate with `↑/↓`, press `enter` to launch, `→` to change model, and `esc` to quit. The menu provides quick access to:
  * **Run a model** - Start an interactive chat
  * **Launch tools** - Claude Code, Codex, OpenClaw, and more
  * **Additional integrations** - Available under “More…”


##
[​](https://docs.ollama.com/quickstart#assistants)
Assistants
Launch [OpenClaw](https://docs.ollama.com/integrations/openclaw), a personal AI with 100+ skills:

```
ollama launch openclaw

```

##
[​](https://docs.ollama.com/quickstart#coding)
Coding
Launch [Claude Code](https://docs.ollama.com/integrations/claude-code) and other coding tools with Ollama models:

```
ollama launch claude

```


```
ollama launch codex

```


```
ollama launch opencode

```

See [integrations](https://docs.ollama.com/integrations) for all supported tools.
##
[​](https://docs.ollama.com/quickstart#api)
API
Use the [API](https://docs.ollama.com/api) to integrate Ollama into your applications:

```
curl http://localhost:11434/api/chat -d '{
  "model": "gemma3",
  "messages": [{ "role": "user", "content": "Hello!" }]
}'

```

See the [API documentation](https://docs.ollama.com/api) for Python, JavaScript, and other integrations.
[Previous](https://docs.ollama.com/)[ Cloud Next ](https://docs.ollama.com/cloud)
⌘I
On this page
  * [Get Started](https://docs.ollama.com/quickstart#get-started)
  * [Assistants](https://docs.ollama.com/quickstart#assistants)
  * [Coding](https://docs.ollama.com/quickstart#coding)
  * [API](https://docs.ollama.com/quickstart#api)


--- DOCUMENT: https://docs.ollama.com/troubleshooting ---
# Troubleshooting
Copy page
How to troubleshoot issues encountered with Ollama
Copy page
Sometimes Ollama may not perform as expected. One of the best ways to figure out what happened is to take a look at the logs. Find the logs on **Mac** by running the command:

```
cat ~/.ollama/logs/server.log

```

On **Linux** systems with systemd, the logs can be found with this command:

```
journalctl -u ollama --no-pager --follow --pager-end

```

When you run Ollama in a **container** , the logs go to stdout/stderr in the container:

```
docker logs <container-name>

```

(Use `docker ps` to find the container name) If manually running `ollama serve` in a terminal, the logs will be on that terminal. When you run Ollama on **Windows** , there are a few different locations. You can view them in the explorer window by hitting `<cmd>+R` and type in:
  * `explorer %LOCALAPPDATA%\Ollama` to view logs. The most recent server logs will be in `server.log` and older logs will be in `server-#.log`
  * `explorer %LOCALAPPDATA%\Programs\Ollama` to browse the binaries (The installer adds this to your user PATH)
  * `explorer %HOMEPATH%\.ollama` to browse where models and configuration is stored
  * `explorer %TEMP%` where temporary executable files are stored in one or more `ollama*` directories

To enable additional debug logging to help troubleshoot problems, first **Quit the running app from the tray menu** then in a powershell terminal

```
$env:OLLAMA_DEBUG="1"
& "ollama app.exe"

```

Join the [Discord](https://discord.gg/ollama) for help interpreting the logs.
##
[​](https://docs.ollama.com/troubleshooting#llm-libraries)
LLM libraries
Ollama includes multiple LLM libraries compiled for different GPUs and CPU vector features. Ollama tries to pick the best one based on the capabilities of your system. If this autodetection has problems, or you run into other problems (e.g. crashes in your GPU) you can workaround this by forcing a specific LLM library. `cpu_avx2` will perform the best, followed by `cpu_avx` an the slowest but most compatible is `cpu`. Rosetta emulation under MacOS will work with the `cpu` library. In the server log, you will see a message that looks something like this (varies from release to release):

```
Dynamic LLM libraries [rocm_v6 cpu cpu_avx cpu_avx2 cuda_v11 rocm_v5]

```

**Experimental LLM Library Override** You can set OLLAMA_LLM_LIBRARY to any of the available LLM libraries to bypass autodetection, so for example, if you have a CUDA card, but want to force the CPU LLM library with AVX2 vector support, use:

```
OLLAMA_LLM_LIBRARY="cpu_avx2" ollama serve

```

You can see what features your CPU has with the following.

```
cat /proc/cpuinfo| grep flags | head -1

```

##
[​](https://docs.ollama.com/troubleshooting#installing-older-or-pre-release-versions-on-linux)
Installing older or pre-release versions on Linux
If you run into problems on Linux and want to install an older version, or you’d like to try out a pre-release before it’s officially released, you can tell the install script which version to install.

```
curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.5.7 sh

```

##
[​](https://docs.ollama.com/troubleshooting#linux-tmp-noexec)
Linux tmp noexec
If your system is configured with the “noexec” flag where Ollama stores its temporary executable files, you can specify an alternate location by setting OLLAMA_TMPDIR to a location writable by the user ollama runs as. For example OLLAMA_TMPDIR=/usr/share/ollama/
##
[​](https://docs.ollama.com/troubleshooting#linux-docker)
Linux docker
If Ollama initially works on the GPU in a docker container, but then switches to running on CPU after some period of time with errors in the server log reporting GPU discovery failures, this can be resolved by disabling systemd cgroup management in Docker. Edit `/etc/docker/daemon.json` on the host and add `"exec-opts": ["native.cgroupdriver=cgroupfs"]` to the docker configuration.
##
[​](https://docs.ollama.com/troubleshooting#nvidia-gpu-discovery)
NVIDIA GPU Discovery
When Ollama starts up, it takes inventory of the GPUs present in the system to determine compatibility and how much VRAM is available. Sometimes this discovery can fail to find your GPUs. In general, running the latest driver will yield the best results.
###
[​](https://docs.ollama.com/troubleshooting#linux-nvidia-troubleshooting)
Linux NVIDIA Troubleshooting
If you are using a container to run Ollama, make sure you’ve set up the container runtime first as described in [docker](https://docs.ollama.com/docker) Sometimes the Ollama can have difficulties initializing the GPU. When you check the server logs, this can show up as various error codes, such as “3” (not initialized), “46” (device unavailable), “100” (no device), “999” (unknown), or others. The following troubleshooting techniques may help resolve the problem
  * If you are using a container, is the container runtime working? Try `docker run --gpus all ubuntu nvidia-smi` - if this doesn’t work, Ollama won’t be able to see your NVIDIA GPU.
  * Is the uvm driver loaded? `sudo nvidia-modprobe -u`
  * Try reloading the nvidia_uvm driver - `sudo rmmod nvidia_uvm` then `sudo modprobe nvidia_uvm`
  * Try rebooting
  * Make sure you’re running the latest nvidia drivers

If none of those resolve the problem, gather additional information and file an issue:
  * Set `CUDA_ERROR_LEVEL=50` and try again to get more diagnostic logs
  * Check dmesg for any errors `sudo dmesg | grep -i nvrm` and `sudo dmesg | grep -i nvidia`


##
[​](https://docs.ollama.com/troubleshooting#amd-gpu-discovery)
AMD GPU Discovery
On linux, AMD GPU access typically requires `video` and/or `render` group membership to access the `/dev/kfd` device. If permissions are not set up correctly, Ollama will detect this and report an error in the server log. When running in a container, in some Linux distributions and container runtimes, the ollama process may be unable to access the GPU. Use `ls -lnd /dev/kfd /dev/dri /dev/dri/*` on the host system to determine the **numeric** group IDs on your system, and pass additional `--group-add ...` arguments to the container so it can access the required devices. For example, in the following output `crw-rw---- 1 0  44 226,   0 Sep 16 16:55 /dev/dri/card0` the group ID column is `44` If you are experiencing problems getting Ollama to correctly discover or use your GPU for inference, the following may help isolate the failure.
  * `AMD_LOG_LEVEL=3` Enable info log levels in the AMD HIP/ROCm libraries. This can help show more detailed error codes that can help troubleshoot problems
  * `OLLAMA_DEBUG=1` During GPU discovery additional information will be reported
  * Check dmesg for any errors from amdgpu or kfd drivers `sudo dmesg | grep -i amdgpu` and `sudo dmesg | grep -i kfd`


###
[​](https://docs.ollama.com/troubleshooting#amd-driver-version-mismatch)
AMD Driver Version Mismatch
If your AMD GPU is not detected on Linux and the server logs contain messages like:

```
msg="failure during GPU discovery" ... error="failed to finish discovery before timeout"
msg="bootstrap discovery took" duration=30s ...

```

This typically means the system’s AMD GPU driver is too old. Ollama bundles ROCm 7 linux libraries which require a compatible ROCm 7 kernel driver. If the system is running an older driver (ROCm 6.x or earlier), GPU initialization will hang during device discovery and eventually time out, causing Ollama to fall back to CPU. To resolve this, upgrade to the ROCm v7 driver using the `amdgpu-install` utility from [AMD’s ROCm documentation](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/). After upgrading, reboot and restart Ollama.
##
[​](https://docs.ollama.com/troubleshooting#multiple-amd-gpus)
Multiple AMD GPUs
If you experience gibberish responses when models load across multiple AMD GPUs on Linux, see the following guide.
  * <https://rocm.docs.amd.com/projects/radeon/en/latest/docs/install/native_linux/mgpu.html#mgpu-known-issues-and-limitations>


##
[​](https://docs.ollama.com/troubleshooting#windows-terminal-errors)
Windows Terminal Errors
Older versions of Windows 10 (e.g., 21H1) are known to have a bug where the standard terminal program does not display control characters correctly. This can result in a long string of strings like `←[?25h←[?25l` being displayed, sometimes erroring with `The parameter is incorrect` To resolve this problem, please update to Win 10 22H1 or newer.
[ Previous Hardware support ](https://docs.ollama.com/gpu)
⌘I
On this page
  * [LLM libraries](https://docs.ollama.com/troubleshooting#llm-libraries)
  * [Installing older or pre-release versions on Linux](https://docs.ollama.com/troubleshooting#installing-older-or-pre-release-versions-on-linux)
  * [Linux tmp noexec](https://docs.ollama.com/troubleshooting#linux-tmp-noexec)
  * [Linux docker](https://docs.ollama.com/troubleshooting#linux-docker)
  * [NVIDIA GPU Discovery](https://docs.ollama.com/troubleshooting#nvidia-gpu-discovery)
  * [Linux NVIDIA Troubleshooting](https://docs.ollama.com/troubleshooting#linux-nvidia-troubleshooting)
  * [AMD GPU Discovery](https://docs.ollama.com/troubleshooting#amd-gpu-discovery)
  * [AMD Driver Version Mismatch](https://docs.ollama.com/troubleshooting#amd-driver-version-mismatch)
  * [Multiple AMD GPUs](https://docs.ollama.com/troubleshooting#multiple-amd-gpus)
  * [Windows Terminal Errors](https://docs.ollama.com/troubleshooting#windows-terminal-errors)


--- DOCUMENT: https://docs.ollama.com/windows ---
# Windows
Copy page
Copy page
Ollama runs as a native Windows application, including NVIDIA and AMD Radeon GPU support. After installing Ollama for Windows, Ollama will run in the background and the `ollama` command line is available in `cmd`, `powershell` or your favorite terminal application. As usual the Ollama [API](https://docs.ollama.com/api) will be served on `http://localhost:11434`.
##
[​](https://docs.ollama.com/windows#system-requirements)
System Requirements
  * Windows 10 22H2 or newer, Home or Pro
  * NVIDIA 452.39 or newer Drivers if you have an NVIDIA card
  * AMD Radeon Driver <https://www.amd.com/en/support> if you have a Radeon card

Ollama uses unicode characters for progress indication, which may render as unknown squares in some older terminal fonts in Windows 10. If you see this, try changing your terminal font settings.
##
[​](https://docs.ollama.com/windows#filesystem-requirements)
Filesystem Requirements
The Ollama install does not require Administrator, and installs in your home directory by default. You’ll need at least 4GB of space for the binary install. Once you’ve installed Ollama, you’ll need additional space for storing the Large Language models, which can be tens to hundreds of GB in size. If your home directory doesn’t have enough space, you can change where the binaries are installed, and where the models are stored.
###
[​](https://docs.ollama.com/windows#changing-install-location)
Changing Install Location
To install the Ollama application in a location different than your home directory, start the installer with the following flag

```
OllamaSetup.exe /DIR="d:\some\location"

```

###
[​](https://docs.ollama.com/windows#changing-model-location)
Changing Model Location
To change where Ollama stores the downloaded models instead of using your home directory, set the environment variable `OLLAMA_MODELS` in your user account.
  1. Start the Settings (Windows 11) or Control Panel (Windows 10) application and search for _environment variables_.
  2. Click on _Edit environment variables for your account_.
  3. Edit or create a new variable for your user account for `OLLAMA_MODELS` where you want the models stored
  4. Click OK/Apply to save.

If Ollama is already running, Quit the tray application and relaunch it from the Start menu, or a new terminal started after you saved the environment variables.
##
[​](https://docs.ollama.com/windows#api-access)
API Access
Here’s a quick example showing API access from `powershell`

```
(Invoke-WebRequest -method POST -Body '{"model":"llama3.2", "prompt":"Why is the sky blue?", "stream": false}' -uri http://localhost:11434/api/generate ).Content | ConvertFrom-json

```

##
[​](https://docs.ollama.com/windows#troubleshooting)
Troubleshooting
Ollama on Windows stores files in a few different locations. You can view them in the explorer window by hitting `<Ctrl>+R` and type in:
  * `explorer %LOCALAPPDATA%\Ollama` contains logs, and downloaded updates
    * _app.log_ contains most resent logs from the GUI application
    * _server.log_ contains the most recent server logs
    * _upgrade.log_ contains log output for upgrades
  * `explorer %LOCALAPPDATA%\Programs\Ollama` contains the binaries (The installer adds this to your user PATH)
  * `explorer %HOMEPATH%\.ollama` contains models and configuration
  * `explorer %TEMP%` contains temporary executable files in one or more `ollama*` directories


##
[​](https://docs.ollama.com/windows#uninstall)
Uninstall
The Ollama Windows installer registers an Uninstaller application. Under `Add or remove programs` in Windows Settings, you can uninstall Ollama.
If you have [changed the OLLAMA_MODELS location](https://docs.ollama.com/windows#changing-model-location), the installer will not remove your downloaded models
##
[​](https://docs.ollama.com/windows#standalone-cli)
Standalone CLI
The easiest way to install Ollama on Windows is to use the `OllamaSetup.exe` installer. It installs in your account without requiring Administrator rights. We update Ollama regularly to support the latest models, and this installer will help you keep up to date. If you’d like to install or integrate Ollama as a service, a standalone `ollama-windows-amd64.zip` zip file is available containing only the Ollama CLI and GPU library dependencies for Nvidia. Depending on your hardware, you may also need to download and extract additional packages into the same directory:
  * **AMD GPU** : `ollama-windows-amd64-rocm.zip`
  * **MLX (CUDA)** : `ollama-windows-amd64-mlx.zip`

This allows for embedding Ollama in existing applications, or running it as a system service via `ollama serve` with tools such as [NSSM](https://nssm.cc/).
If you are upgrading from a prior version, you should remove the old directories first.
[Previous](https://docs.ollama.com/macos)[ Docker Next ](https://docs.ollama.com/docker)
⌘I
On this page
  * [System Requirements](https://docs.ollama.com/windows#system-requirements)
  * [Filesystem Requirements](https://docs.ollama.com/windows#filesystem-requirements)
  * [Changing Install Location](https://docs.ollama.com/windows#changing-install-location)
  * [Changing Model Location](https://docs.ollama.com/windows#changing-model-location)
  * [API Access](https://docs.ollama.com/windows#api-access)
  * [Troubleshooting](https://docs.ollama.com/windows#troubleshooting)
  * [Uninstall](https://docs.ollama.com/windows#uninstall)
  * [Standalone CLI](https://docs.ollama.com/windows#standalone-cli)


