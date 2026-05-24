

--- DOCUMENT: https://pydantic.dev/docs/ ---
# Pydantic Docs
Documentation for the Pydantic stack. Build and validate data with Pydantic Validation, create agents with Pydantic AI, and observe and improve agents in production with Pydantic Logfire.
### [Pydantic Validation Data validation using Python type annotations. Parse and validate complex data, generate JSON schemas, and ensure data integrity. ](https://pydantic.dev/docs/validation/latest/concepts/models/)### [Pydantic AI Agent framework for building production AI applications. Type-safe, structured outputs, tool use, multi-agent orchestration with native Logfire integration. ](https://pydantic.dev/docs/ai/overview/)### [Pydantic Logfire General and AI observability to monitor LLM calls, agent behavior, costs, and service performance across your entire stack. ](https://pydantic.dev/docs/logfire/get-started/)
© Pydantic Services Inc. 2025 to present
[ ](https://github.com/pydantic "Pydantic on GitHub") [ ](https://x.com/pydantic "Pydantic on X") [ ](https://www.linkedin.com/company/pydantic/ "Pydantic on LinkedIn") [ ](https://bsky.app/profile/pydantic.dev "Pydantic on Bluesky")


--- DOCUMENT: https://pydantic.dev/docs/ai/overview/ ---
# Pydantic AI
![Pydantic AI](https://pydantic.dev/docs/ai/img/pydantic-ai-dark.svg)
![Pydantic AI](https://pydantic.dev/docs/ai/img/pydantic-ai-light.svg)
_GenAI Agent Framework, the Pydantic way_
[![CI](https://github.com/pydantic/pydantic-ai/actions/workflows/ci.yml/badge.svg?event=push)](https://github.com/pydantic/pydantic-ai/actions/workflows/ci.yml?query=branch%3Amain)[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/pydantic/pydantic-ai.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/pydantic/pydantic-ai)[![PyPI](https://img.shields.io/pypi/v/pydantic-ai.svg)](https://pypi.python.org/pypi/pydantic-ai)[![versions](https://img.shields.io/pypi/pyversions/pydantic-ai.svg)](https://github.com/pydantic/pydantic-ai)[![license](https://img.shields.io/github/license/pydantic/pydantic-ai.svg)](https://github.com/pydantic/pydantic-ai/blob/main/LICENSE)[![Join Slack](https://img.shields.io/badge/Slack-Join%20Slack-4A154B?logo=slack)](https://logfire.pydantic.dev/docs/join-slack/)
Pydantic AI is a Python agent framework designed to help you quickly, confidently, and painlessly build production grade applications and workflows with Generative AI.
FastAPI revolutionized web development by offering an innovative and ergonomic design, built on the foundation of [Pydantic Validation](https://docs.pydantic.dev) and modern Python features like type hints.
Yet despite virtually every Python agent framework and LLM library using Pydantic Validation, when we began to use LLMs in [Pydantic Logfire](https://pydantic.dev/logfire), we couldn’t find anything that gave us the same feeling.
We built Pydantic AI with one simple aim: to bring that FastAPI feeling to GenAI app and agent development.
## Why use Pydantic AI
[](https://pydantic.dev/docs/ai/overview/#why-use-pydantic-ai)
  1. **Built by the Pydantic Team** : [Pydantic Validation](https://docs.pydantic.dev/latest/) is the validation layer of the OpenAI SDK, the Google ADK, the Anthropic SDK, LangChain, LlamaIndex, AutoGPT, Transformers, CrewAI, Instructor and many more. _Why use the derivative when you can go straight to the source?_ 😃
  2. **Model-agnostic** : Supports virtually every [model](https://pydantic.dev/docs/ai/models/overview) and provider: OpenAI, Anthropic, Gemini, DeepSeek, Grok, Cohere, Mistral, and Perplexity; Azure AI Foundry, Amazon Bedrock, Google Vertex AI, Ollama, LiteLLM, Groq, OpenRouter, Together AI, Fireworks AI, Cerebras, Hugging Face, GitHub, Heroku, Vercel, Nebius, OVHcloud, Alibaba Cloud, SambaNova, and Outlines. If your favorite model or provider is not listed, you can easily implement a [custom model](https://pydantic.dev/docs/ai/models/overview#custom-models).
  3. **Seamless Observability** : Tightly [integrates](https://pydantic.dev/docs/ai/integrations/logfire) with [Pydantic Logfire](https://pydantic.dev/logfire), our general-purpose OpenTelemetry observability platform, for real-time debugging, evals-based performance monitoring, and behavior, tracing, and cost tracking. If you already have an observability platform that supports OTel, you can [use that too](https://pydantic.dev/docs/ai/integrations/logfire#alternative-observability-backends).
  4. **Fully Type-safe** : Designed to give your IDE or AI coding agent as much context as possible for auto-completion and [type checking](https://pydantic.dev/docs/ai/core-concepts/agent#static-type-checking), moving entire classes of errors from runtime to write-time for a bit of that Rust “if it compiles, it works” feel.
  5. **Powerful Evals** : Enables you to systematically test and [evaluate](https://pydantic.dev/docs/ai/evals/) the performance and accuracy of the agentic systems you build, and monitor the performance over time in Pydantic Logfire.
  6. **Extensible by Design** : Build agents from composable [capabilities](https://pydantic.dev/docs/ai/core-concepts/capabilities) that bundle tools, hooks, instructions, and model settings into reusable units. Use built-in capabilities for [web search](https://pydantic.dev/docs/ai/core-concepts/capabilities#provider-adaptive-tools), [thinking](https://pydantic.dev/docs/ai/core-concepts/capabilities#thinking), and [MCP](https://pydantic.dev/docs/ai/core-concepts/capabilities#provider-adaptive-tools), pick from the [Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/overview) capability library, build your own, or install [third-party capability packages](https://pydantic.dev/docs/ai/guides/extensibility). Define agents entirely in [YAML/JSON](https://pydantic.dev/docs/ai/core-concepts/agent-spec) — no code required.
  7. **MCP, A2A, and UI** : Integrates the [Model Context Protocol](https://pydantic.dev/docs/ai/mcp/overview), [Agent2Agent](https://pydantic.dev/docs/ai/integrations/a2a), and various [UI event stream](https://pydantic.dev/docs/ai/integrations/ui/overview) standards to give your agent access to external tools and data, let it interoperate with other agents, and build interactive applications with streaming event-based communication.
  8. **Human-in-the-Loop Tool Approval** : Easily lets you flag that certain tool calls [require approval](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools#human-in-the-loop-tool-approval) before they can proceed, possibly depending on tool call arguments, conversation history, or user preferences.
  9. **Durable Execution** : Enables you to build [durable agents](https://pydantic.dev/docs/ai/integrations/durable_execution/overview) that can preserve their progress across transient API failures and application errors or restarts, and handle long-running, asynchronous, and human-in-the-loop workflows with production-grade reliability.
  10. **Streamed Outputs** : Provides the ability to [stream](https://pydantic.dev/docs/ai/core-concepts/output#streamed-results) structured output continuously, with immediate validation, ensuring real time access to generated data.
  11. **Graph Support** : Provides a powerful way to define [graphs](https://pydantic.dev/docs/ai/graph/) using type hints, for use in complex applications where standard control flow can degrade to spaghetti code.


Realistically though, no list is going to be as convincing as [giving it a try](https://pydantic.dev/docs/ai/overview/#next-steps) and seeing how it makes you feel!
**Sign up for our newsletter,_The Pydantic Stack_ , with updates & tutorials on Pydantic AI, Logfire, and Pydantic:**
Subscribe
## Hello World Example
[](https://pydantic.dev/docs/ai/overview/#hello-world-example)
Here’s a minimal example of Pydantic AI:
hello_world.pyDirectGateway
```
from pydantic_ai import Agentagent = Agent(    'anthropic:claude-sonnet-4-6',  instructions='Be concise, reply with one sentence.',  )result = agent.run_sync('Where does "hello world" come from?')  print(result.output)"""The first known use of "hello, world" was in a 1974 textbook about the C programming language."""


```

We configure the agent to use [Anthropic's Claude Sonnet 4.6](https://pydantic.dev/docs/ai/models/anthropic) model, but you can also set the model when running the agent.
Register static [instructions](https://pydantic.dev/docs/ai/core-concepts/agent#instructions) using a keyword argument to the agent.
[Run the agent](https://pydantic.dev/docs/ai/core-concepts/agent#running-agents) synchronously, starting a conversation with the LLM.
_(This example is complete, it can be run “as is”, assuming you’ve[installed the `pydantic_ai` package](https://pydantic.dev/docs/ai/overview/install))_
The exchange will be very short: Pydantic AI will send the instructions and the user prompt to the LLM, and the model will return a text response.
Not very interesting yet, but we can easily add [tools](https://pydantic.dev/docs/ai/tools-toolsets/tools), [dynamic instructions](https://pydantic.dev/docs/ai/core-concepts/agent#instructions), [structured outputs](https://pydantic.dev/docs/ai/core-concepts/output), or composable [capabilities](https://pydantic.dev/docs/ai/core-concepts/capabilities) to build more powerful agents.
Here’s the same agent with [thinking](https://pydantic.dev/docs/ai/core-concepts/capabilities#thinking) and [web search](https://pydantic.dev/docs/ai/core-concepts/capabilities#provider-adaptive-tools) capabilities:
hello_world_capabilities.pyDirectGateway
```
from pydantic_ai import Agentfrom pydantic_ai.capabilities import Thinking, WebSearchagent = Agent(    'anthropic:claude-sonnet-4-6',    instructions='Be concise, reply with one sentence.',    capabilities=[Thinking(), WebSearch()],)result = agent.run_sync('What was the mass of the largest meteorite found this year?')print(result.output)"""The largest meteorite recovered this year weighed approximately 7.6 kg, found in the Sahara Desert in January."""


```

## Tools & Dependency Injection Example
[](https://pydantic.dev/docs/ai/overview/#tools--dependency-injection-example)
Here is a concise example using Pydantic AI to build a support agent for a bank:
bank_support.pyDirectGateway
```
from dataclasses import dataclassfrom pydantic import BaseModel, Fieldfrom pydantic_ai import Agent, RunContextfrom bank_database import DatabaseConn@dataclassclass SupportDependencies:    customer_id: int  db: DatabaseConn  class SupportOutput(BaseModel):    support_advice: str = Field(description='Advice returned to the customer')  block_card: bool = Field(description="Whether to block the customer's card")  risk: int = Field(description='Risk level of query', ge=0, le=10)support_agent = Agent(    'openai:gpt-5.2',    deps_type=SupportDependencies,  output_type=SupportOutput,    instructions=(        'You are a support agent in our bank, give the '      'customer support and judge the risk level of their query.'  ),)@support_agent.instructions  async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:  customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)  return f"The customer's name is {customer_name!r}"@support_agent.tool  async def customer_balance(  ctx: RunContext[SupportDependencies], include_pending: bool) -> float:  """Returns the customer's current account balance."""    return await ctx.deps.db.customer_balance(      id=ctx.deps.customer_id,      include_pending=include_pending,  )...  async def main():  deps = SupportDependencies(customer_id=123, db=DatabaseConn())  result = await support_agent.run('What is my balance?', deps=deps)    print(result.output)    """  support_advice='Hello John, your current account balance, including pending transactions, is $123.45.' block_card=False risk=1  """  result = await support_agent.run('I just lost my card!', deps=deps)  print(result.output)  """  support_advice="I'm sorry to hear that, John. We are temporarily blocking your card to prevent unauthorized transactions." block_card=True risk=8  """


```

This [agent](https://pydantic.dev/docs/ai/core-concepts/agent) will act as first-tier support in a bank. Agents are generic in the type of dependencies they accept and the type of output they return. In this case, the support agent has type `Agent[SupportDependencies, SupportOutput]`.
Here we configure the agent to use [OpenAI's GPT-5 model](https://pydantic.dev/docs/ai/models/openai), you can also set the model when running the agent.
The `SupportDependencies` dataclass is used to pass data, connections, and logic into the model that will be needed when running [instructions](https://pydantic.dev/docs/ai/core-concepts/agent#instructions) and [tool](https://pydantic.dev/docs/ai/tools-toolsets/tools) functions. Pydantic AI's system of dependency injection provides a [type-safe](https://pydantic.dev/docs/ai/core-concepts/agent#static-type-checking) way to customise the behavior of your agents, and can be especially useful when running [unit tests](https://pydantic.dev/docs/ai/guides/testing) and evals.
Static [instructions](https://pydantic.dev/docs/ai/core-concepts/agent#instructions) can be registered with the [`instructions` keyword argument](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.__init__) to the agent.
Dynamic [instructions](https://pydantic.dev/docs/ai/core-concepts/agent#instructions) can be registered with the [`@agent.instructions`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.instructions) decorator, and can make use of dependency injection. Dependencies are carried via the [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) argument, which is parameterized with the `deps_type` from above. If the type annotation here is wrong, static type checkers will catch it.
The [`@agent.tool`](https://pydantic.dev/docs/ai/tools-toolsets/tools) decorator let you register functions which the LLM may call while responding to a user. Again, dependencies are carried via [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext), any other arguments become the tool schema passed to the LLM. Pydantic is used to validate these arguments, and errors are passed back to the LLM so it can retry.
The docstring of a tool is also passed to the LLM as the description of the tool. Parameter descriptions are [extracted](https://pydantic.dev/docs/ai/tools-toolsets/tools#function-tools-and-schema) from the docstring and added to the parameter schema sent to the LLM.
[Run the agent](https://pydantic.dev/docs/ai/core-concepts/agent#running-agents) asynchronously, conducting a conversation with the LLM until a final response is reached. Even in this fairly simple case, the agent will exchange multiple messages with the LLM as tools are called to retrieve an output.
The response from the agent will be guaranteed to be a `SupportOutput`. If validation fails [reflection](https://pydantic.dev/docs/ai/core-concepts/agent#reflection-and-self-correction), the agent is prompted to try again.
The output will be validated with Pydantic to guarantee it is a `SupportOutput`, since the agent is generic, it'll also be typed as a `SupportOutput` to aid with static type checking.
In a real use case, you'd add more tools and longer instructions to the agent to extend the context it's equipped with and support it can provide.
This is a simple sketch of a database connection, used to keep the example short and readable. In reality, you'd be connecting to an external database (e.g. PostgreSQL) to get information about customers.
This [Pydantic](https://docs.pydantic.dev) model is used to constrain the structured data returned by the agent. From this simple definition, Pydantic builds the JSON Schema that tells the LLM how to return the data, and performs validation to guarantee the data is correct at the end of the run.
`bank_support.py` example
The code included here is incomplete for the sake of brevity (the definition of `DatabaseConn` is missing); you can find the complete `bank_support.py` example [here](https://pydantic.dev/docs/ai/examples/bank-support).
## Instrumentation with Pydantic Logfire
[](https://pydantic.dev/docs/ai/overview/#instrumentation-with-pydantic-logfire)
Even a simple agent with just a handful of tools can result in a lot of back-and-forth with the LLM, making it nearly impossible to be confident of what’s going on just from reading the code. To understand the flow of the above runs, we can watch the agent in action using Pydantic Logfire.
To do this, we need to [set up Logfire](https://pydantic.dev/docs/ai/integrations/logfire#using-logfire), and add the following to our code:
bank_support_with_logfire.pyDirectGateway
```
...from pydantic_ai import Agent, RunContextfrom bank_database import DatabaseConnimport logfirelogfire.configure()  logfire.instrument_pydantic_ai()  logfire.instrument_sqlite3()  ...support_agent = Agent(  'openai:gpt-5.2',  deps_type=SupportDependencies,  output_type=SupportOutput,  instructions=(      'You are a support agent in our bank, give the '      'customer support and judge the risk level of their query.'  ),)


```

Configure the Logfire SDK, this will fail if project is not set up.
This will instrument all Pydantic AI agents used from here on out. If you want to instrument only a specific agent, you can pass the [`instrument=True` keyword argument](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.__init__) to the agent.
In our demo, `DatabaseConn` uses [`sqlite3`](https://docs.python.org/3/library/sqlite3.html#module-sqlite3) to connect to a PostgreSQL database, so [`logfire.instrument_sqlite3()`](https://logfire.pydantic.dev/docs/integrations/databases/sqlite3/) is used to log the database queries.
That’s enough to get the following view of your agent in action:
Logfire instrumentation for the bank agent — [ View in Logfire](https://logfire-eu.pydantic.dev/public-trace/a2957caa-b7b7-4883-a529-777742649004?spanId=31aade41ab896144)
See [Monitoring and Performance](https://pydantic.dev/docs/ai/integrations/logfire) to learn more.
## `llms.txt`
[](https://pydantic.dev/docs/ai/overview/#llmstxt)
The Pydantic AI documentation is available in the [llms.txt](https://llmstxt.org/) format. This format is defined in Markdown and suited for LLMs and AI coding assistants and agents.
Two formats are available:
  * [`llms.txt`](https://ai.pydantic.dev/llms.txt): a file containing a brief description of the project, along with links to the different sections of the documentation. The structure of this file is described in details [here](https://llmstxt.org/#format).
  * [`llms-full.txt`](https://ai.pydantic.dev/llms-full.txt): Similar to the `llms.txt` file, but every link content is included. Note that this file may be too large for some LLMs.


As of today, these files are not automatically leveraged by IDEs or coding agents, but they will use it if you provide a link or the full text.
## Next Steps
[](https://pydantic.dev/docs/ai/overview/#next-steps)
To try Pydantic AI for yourself, [install it](https://pydantic.dev/docs/ai/overview/install) and follow the instructions [in the examples](https://pydantic.dev/docs/ai/examples/setup).
Read the [docs](https://pydantic.dev/docs/ai/core-concepts/agent) to learn more about building applications with Pydantic AI.
Read the [API Reference](https://pydantic.dev/docs/ai/api/pydantic-ai/agent) to understand Pydantic AI’s interface.
Join [Slack](https://logfire.pydantic.dev/docs/join-slack/) or file an issue on [](https://github.com/pydantic/pydantic-ai/issues) if you have any questions.
Was this page helpful? Thanks for your feedback!
[ Previous
Visual studio code ](https://pydantic.dev/docs/validation/1.10/extras/visual_studio_code/) [ Next
Installation ](https://pydantic.dev/docs/ai/overview/install/)
© Pydantic Services Inc. 2025 to present
[ ](https://github.com/pydantic "Pydantic on GitHub") [ ](https://x.com/pydantic "Pydantic on X") [ ](https://www.linkedin.com/company/pydantic/ "Pydantic on LinkedIn") [ ](https://bsky.app/profile/pydantic.dev "Pydantic on Bluesky")


--- DOCUMENT: https://pydantic.dev/docs/logfire/get-started/ ---
# Logfire
[![CI](https://github.com/pydantic/logfire/actions/workflows/main.yml/badge.svg?event=push)](https://github.com/pydantic/logfire/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)[![codecov](https://codecov.io/gh/pydantic/logfire/graph/badge.svg?token=735CNGCGFD)](https://codecov.io/gh/pydantic/logfire)[![pypi](https://img.shields.io/pypi/v/logfire.svg)](https://pypi.python.org/pypi/logfire)[![license](https://img.shields.io/github/license/pydantic/logfire.svg)](https://github.com/pydantic/logfire/blob/main/LICENSE)[![versions](https://img.shields.io/pypi/pyversions/logfire.svg)](https://github.com/pydantic/logfire)[![Join Slack](https://img.shields.io/badge/Slack-Join%20Slack-4A154B?logo=slack)](https://pydantic.dev/docs/logfire/get-started/join-slack/)
## About Pydantic Logfire
[](https://pydantic.dev/docs/logfire/get-started/#about-pydantic-logfire)
From the team behind **Pydantic Validation** , **Pydantic Logfire** is a new type of observability platform built on the same belief as our open source library — that the most powerful tools can be easy to use.
**Logfire** is built on OpenTelemetry, with native SDKs for **Python** , **JavaScript/TypeScript** , and **Rust** — plus support for **any language** via OpenTelemetry. [Read more](https://pydantic.dev/docs/logfire/get-started/why).
This page walks through setting up a Python app. For other languages, see the [JavaScript/TypeScript](https://pydantic.dev/docs/logfire/integrations/javascript/) integration or our [language support](https://pydantic.dev/docs/logfire/resources/languages) page.
  1. [Set up Logfire](https://pydantic.dev/docs/logfire/get-started/#logfire)
  2. [Install the SDK](https://pydantic.dev/docs/logfire/get-started/#sdk)
  3. [Instrument your project](https://pydantic.dev/docs/logfire/get-started/#instrument)


## Set up Logfire
[](https://pydantic.dev/docs/logfire/get-started/#logfire)
  1. [Log into Logfire ](https://logfire.pydantic.dev/login)
  2. Follow the prompts to create your account
  3. Once logged in, you’ll see the **Welcome to Logfire** prompt. Click **Let’s go!** to go to the **starter-project** Setup page.
  4. You will find how to send data to your **starter-project** there. Also, there are some code snippets to help you get started.


A **Logfire** project is a namespace for organizing your data. All data sent to **Logfire** must be associated with a project.
Ready to create your own projects in UI or CLI?
  * In the UI, create projects by navigating to the Organization > Projects page, and click **New project**.
  * For CLI check the [SDK CLI documentation](https://pydantic.dev/docs/logfire/reference/cli#create-projects-new).


## Install the SDK
[](https://pydantic.dev/docs/logfire/get-started/#sdk)
  1. In the terminal, install the **Logfire** SDK (Software Developer Kit):


  * [ pip ](https://pydantic.dev/docs/logfire/get-started/#tab-panel-114)
  * [ uv ](https://pydantic.dev/docs/logfire/get-started/#tab-panel-115)
  * [ conda ](https://pydantic.dev/docs/logfire/get-started/#tab-panel-116)


Terminal
```
pip install logfire


```

Terminal
```
uv add logfire


```

Terminal
```
conda install -c conda-forge logfire


```

  1. Once installed, try it out!

Terminal
```
logfire -h


```

  1. Next, authenticate your local environment:

Terminal
```
logfire auth


```

Upon successful authentication, credentials are stored in `~/.logfire/default.toml`.
## Instrument your project
[](https://pydantic.dev/docs/logfire/get-started/#instrument)
  * [ Development ](https://pydantic.dev/docs/logfire/get-started/#tab-panel-117)
  * [ Production ](https://pydantic.dev/docs/logfire/get-started/#tab-panel-118)


During development, we recommend using the CLI to configure Logfire. You can also use a [write token](https://pydantic.dev/docs/logfire/manage/create-write-tokens).
  1. Set your project

in the terminal:
```
logfire projects use <first-project>


```

Run this command from the root directory of your app, e.g. `~/projects/first-project`
  1. Write some basic logs in your Python app


hello_world.py
```
import logfirelogfire.configure()  logfire.info('Hello, {name}!', name='world')


```

The `configure()` method should be called once before logging to initialize **Logfire**.
This will log `Hello world!` with `info` level.
Other [log levels](https://pydantic.dev/docs/logfire/api/logfire/#logfire.Logfire) are also available to use, including `trace`, `debug`, `notice`, `warn`, `error`, and `fatal`.
  1. See your logs in the **Live** view


![Hello world screenshot](https://pydantic.dev/docs/logfire/images/logfire-screenshot-first-steps-hello-world.png)
In production, we recommend you provide your write token to the Logfire SDK via environment variables.
  1. Generate a new write token in the **Logfire** platform
     * Go to Project
     * Follow the prompts to create a new token
  2. Configure your **Logfire** environment

In the terminal:
```
export LOGFIRE_TOKEN=<your-write-token>


```

Running this command stores a Write Token used by the SDK to send data to a file in the current directory, at `.logfire/logfire_credentials.json`
  1. Write some basic logs in your Python app


hello_world.py
```
import logfirelogfire.configure()  logfire.info('Hello, {name}!', name='world')


```

The `configure()` method should be called once before logging to initialize **Logfire**.
This will log `Hello world!` with `info` level.
Other [log levels](https://pydantic.dev/docs/logfire/api/logfire/#logfire.Logfire) are also available to use, including `trace`, `debug`, `notice`, `warn`, `error`, and `fatal`.
  1. See your logs in the **Live** view


![Hello world screenshot](https://pydantic.dev/docs/logfire/images/logfire-screenshot-first-steps-hello-world.png)
* * *
## Next steps
[](https://pydantic.dev/docs/logfire/get-started/#next-steps)
Ready to keep going?
  * Read about [Concepts](https://pydantic.dev/docs/logfire/get-started/concepts)
  * Complete the [Onboarding Checklist](https://pydantic.dev/docs/logfire/instrument/)
  * Building AI applications? See [AI & LLM Observability](https://pydantic.dev/docs/logfire/get-started/ai-observability)


More topics to explore…
  * Logfire’s real power comes from [integrations with many popular libraries](https://pydantic.dev/docs/logfire/integrations/)
  * As well as spans, you can [use Logfire to record metrics](https://pydantic.dev/docs/logfire/instrument/add-metrics)
  * Using another language? See [Language support](https://pydantic.dev/docs/logfire/resources/languages) for Python, JavaScript/TypeScript, Rust, and more
  * Compliance requirements (e.g. SOC2)? [See Logfire’s certifications](https://pydantic.dev/docs/logfire/deploy/compliance)


Was this page helpful? Thanks for your feedback!
[ Previous
Version Policy ](https://pydantic.dev/docs/ai/project/version-policy/) [ Next
Why Logfire? ](https://pydantic.dev/docs/logfire/get-started/why/)
© Pydantic Services Inc. 2025 to present
[ ](https://github.com/pydantic "Pydantic on GitHub") [ ](https://x.com/pydantic "Pydantic on X") [ ](https://www.linkedin.com/company/pydantic/ "Pydantic on LinkedIn") [ ](https://bsky.app/profile/pydantic.dev "Pydantic on Bluesky")


--- DOCUMENT: https://pydantic.dev/docs/validation/latest/concepts/models/ ---
# Models
API Documentation
[`pydantic.main.BaseModel`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel)

One of the primary ways of defining schema in Pydantic is via models. Models are simply classes which inherit from [`BaseModel`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel) and define fields as annotated attributes.
You can think of models as similar to structs in languages like C, or as the requirements of a single endpoint in an API.
Models share many similarities with Python’s [dataclasses](https://docs.python.org/3/library/dataclasses.html#module-dataclasses), but have been designed with some subtle-yet-important differences that streamline certain workflows related to validation, serialization, and JSON schema generation. You can find more discussion of this in the [Dataclasses](https://pydantic.dev/docs/validation/latest/concepts/dataclasses) section of the docs.
Untrusted data can be passed to a model and, after parsing and validation, Pydantic guarantees that the fields of the resultant model instance will conform to the field types defined on the model.
_deliberate_ misnomer
### TL;DR
[](https://pydantic.dev/docs/validation/latest/concepts/models/#tldr)
We use the term “validation” to refer to the process of instantiating a model (or other type) that adheres to specified types and constraints. This task, which Pydantic is well known for, is most widely recognized as “validation” in colloquial terms, even though in other contexts the term “validation” may be more restrictive.
* * *
### The long version
[](https://pydantic.dev/docs/validation/latest/concepts/models/#the-long-version)
The potential confusion around the term “validation” arises from the fact that, strictly speaking, Pydantic’s primary focus doesn’t align precisely with the dictionary definition of “validation”:
> ### validation
> [](https://pydantic.dev/docs/validation/latest/concepts/models/#validation)
> _noun_ the action of checking or proving the validity or accuracy of something.
In Pydantic, the term “validation” refers to the process of instantiating a model (or other type) that adheres to specified types and constraints. Pydantic guarantees the types and constraints of the output, not the input data. This distinction becomes apparent when considering that Pydantic’s `ValidationError` is raised when data cannot be successfully parsed into a model instance.
While this distinction may initially seem subtle, it holds practical significance. In some cases, “validation” goes beyond just model creation, and can include the copying and coercion of data. This can involve copying arguments passed to the constructor in order to perform coercion to a new type without mutating the original input data. For a more in-depth understanding of the implications for your usage, refer to the [Data Conversion](https://pydantic.dev/docs/validation/latest/concepts/models/#data-conversion) and [Attribute Copies](https://pydantic.dev/docs/validation/latest/concepts/models/#attribute-copies) sections below.
In essence, Pydantic’s primary goal is to assure that the resulting structure post-processing (termed “validation”) precisely conforms to the applied type hints. Given the widespread adoption of “validation” as the colloquial term for this process, we will consistently use it in our documentation.
While the terms “parse” and “validation” were previously used interchangeably, moving forward, we aim to exclusively employ “validate”, with “parse” reserved specifically for discussions related to [JSON parsing](https://pydantic.dev/docs/validation/latest/concepts/json).
## Basic model usage
[](https://pydantic.dev/docs/validation/latest/concepts/models/#basic-model-usage)
Pydantic relies heavily on the existing Python typing constructs to define models. If you are not familiar with those, the following resources can be useful:
  * The [Type System Guides](https://typing.readthedocs.io/en/latest/guides/index.html)
  * The [mypy documentation](https://mypy.readthedocs.io/en/latest/)


```
from pydantic import BaseModel, ConfigDictclass User(BaseModel):  id: int  name: str = 'Jane Doe'  model_config = ConfigDict(str_max_length=10)


```

Pydantic models support a variety of [configuration values](https://pydantic.dev/docs/validation/latest/concepts/config) (see [here](https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict) for the available configuration values).
In this example, `User` is a model with two fields:
  * `id`, which is an integer (defined using the [`int`](https://docs.python.org/3/library/functions.html#int) type) and is required
  * `name`, which is a string (defined using the [`str`](https://docs.python.org/3/library/stdtypes.html#str) type) and is not required (it has a default value).


The documentation on [types](https://pydantic.dev/docs/validation/latest/concepts/types) expands on the supported types.
Fields can be customized in a number of ways using the [`Field()`](https://pydantic.dev/docs/validation/latest/api/pydantic/fields/#pydantic.fields.Field) function. See the [documentation on fields](https://pydantic.dev/docs/validation/latest/concepts/fields) for more information.
The model can then be instantiated:

```
user = User(id='123')


```

`user` is an instance of `User`. Initialization of the object will perform all parsing and validation. If no [`ValidationError`](https://pydantic.dev/docs/validation/latest/api/pydantic-core/pydantic_core/#pydantic_core.ValidationError) exception is raised, you know the resulting model instance is valid.
Fields of a model can be accessed as normal attributes of the `user` object:

```
assert user.name == 'Jane Doe'  assert user.id == 123  assert isinstance(user.id, int)


```

`name` wasn't set when `user` was initialized, so the default value was used. The [`model_fields_set`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_fields_set) attribute can be inspected to check the field names explicitly set during instantiation.
Note that the string `'123'` was coerced to an integer and its value is `123`. More details on Pydantic's coercion logic can be found in the [data conversion](https://pydantic.dev/docs/validation/latest/concepts/models/#data-conversion) section.
The model instance can be serialized using the [`model_dump()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_dump) method:

```
assert user.model_dump() == {'id': 123, 'name': 'Jane Doe'}


```

Calling [dict](https://docs.python.org/3/reference/expressions.html#dict) on the instance will also provide a dictionary, but nested fields will not be recursively converted into dictionaries. [`model_dump()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_dump) also provides numerous arguments to customize the serialization result.
By default, models are mutable and field values can be changed through attribute assignment:

```
user.id = 321assert user.id == 321


```

When defining your models, watch out for naming collisions between your field name and its type annotation.
For example, the following will not behave as expected and would yield a validation error:

```
from typing import Optionalfrom pydantic import BaseModelclass Boo(BaseModel):    int: Optional[int] = Nonem = Boo(int=123)  # Will fail to validate.


```

Because of how Python evaluates [annotated assignment statements](https://docs.python.org/3/reference/simple_stmts.html#annassign), the statement is equivalent to `int: None = None`, thus leading to a validation error.
### Model methods and properties
[](https://pydantic.dev/docs/validation/latest/concepts/models/#model-methods-and-properties)
The example above only shows the tip of the iceberg of what models can do. Model classes possess the following methods and attributes:
  * [`model_validate()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_validate): Validates the given object against the Pydantic model. See [Validating data](https://pydantic.dev/docs/validation/latest/concepts/models/#validating-data).
  * [`model_validate_json()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_validate_json): Validates the given JSON data against the Pydantic model. See [Validating data](https://pydantic.dev/docs/validation/latest/concepts/models/#validating-data).
  * [`model_construct()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_construct): Creates models without running validation. See [Creating models without validation](https://pydantic.dev/docs/validation/latest/concepts/models/#creating-models-without-validation).
  * [`model_dump()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_dump): Returns a dictionary of the model’s fields and values. See [Serialization](https://pydantic.dev/docs/validation/latest/concepts/serialization#python-mode).
  * [`model_dump_json()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_dump_json): Returns a JSON string representation of [`model_dump()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_dump). See [Serialization](https://pydantic.dev/docs/validation/latest/concepts/serialization#json-mode).
  * [`model_copy()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_copy): Returns a copy (by default, shallow copy) of the model. See [Model copy](https://pydantic.dev/docs/validation/latest/concepts/models/#model-copy).
  * [`model_json_schema()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_json_schema): Returns a jsonable dictionary representing the model’s JSON Schema. See [JSON Schema](https://pydantic.dev/docs/validation/latest/concepts/json_schema).
  * [`model_fields`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_fields): A mapping between field names and their definitions ([`FieldInfo`](https://pydantic.dev/docs/validation/latest/api/pydantic/fields/#pydantic.fields.FieldInfo) instances).
  * [`model_computed_fields`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_computed_fields): A mapping between computed field names and their definitions ([`ComputedFieldInfo`](https://pydantic.dev/docs/validation/latest/api/pydantic/fields/#pydantic.fields.ComputedFieldInfo) instances).
  * [`model_parametrized_name()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_parametrized_name): Computes the class name for parametrizations of generic classes.
  * [`model_post_init()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_post_init): Performs additional actions after the model is instantiated and all field validators are applied.
  * [`model_rebuild()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_rebuild): Rebuilds the model schema, which also supports building recursive generic models. See [Rebuilding model schema](https://pydantic.dev/docs/validation/latest/concepts/models/#rebuilding-model-schema).


Model instances possess the following attributes:
  * [`model_extra`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_extra): The extra fields set during validation.
  * [`model_fields_set`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_fields_set): The set of fields which were explicitly provided when the model was initialized.


See the API documentation of [`BaseModel`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel) for the class definition including a full list of methods and attributes.
See [Changes to `pydantic.BaseModel`](https://pydantic.dev/docs/validation/latest/get-started/migration#changes-to-pydanticbasemodel) in the [Migration Guide](https://pydantic.dev/docs/validation/latest/get-started/migration) for details on changes from Pydantic V1.
## Data conversion
[](https://pydantic.dev/docs/validation/latest/concepts/models/#data-conversion)
Pydantic may cast input data to force it to conform to model field types, and in some cases this may result in a loss of information. For example:

```
from pydantic import BaseModelclass Model(BaseModel):    a: int    b: float    c: strprint(Model(a=3.000, b='2.72', c=b'binary data').model_dump())#> {'a': 3, 'b': 2.72, 'c': 'binary data'}


```

This is a deliberate decision of Pydantic, and is frequently the most useful approach. See [this issue](https://github.com/pydantic/pydantic/issues/578) for a longer discussion on the subject.
Nevertheless, Pydantic provides a [strict mode](https://pydantic.dev/docs/validation/latest/concepts/strict_mode), where no data conversion is performed. Values must be of the same type as the declared field type.
This is also the case for collections. In most cases, you shouldn’t make use of abstract container classes and just use a concrete type, such as [`list`](https://docs.python.org/3/glossary.html#term-list):

```
from pydantic import BaseModelclass Model(BaseModel):  items: list[int]  print(Model(items=(1, 2, 3)))#> items=[1, 2, 3]


```

In this case, you might be tempted to use the abstract [`Sequence`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence) type to allow both lists and tuples. But Pydantic takes care of converting the tuple input to a list, so in most cases this isn't necessary.
Besides, using these abstract types can also lead to [poor validation performance](https://pydantic.dev/docs/validation/latest/concepts/performance#sequence-vs-list-or-tuple-with-mapping-vs-dict), and in general using concrete container types will avoid unnecessary checks.
## Extra data
[](https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data)
By default, Pydantic models **won’t error when you provide extra data** , and these values will simply be ignored:

```
from pydantic import BaseModelclass Model(BaseModel):    x: intm = Model(x=1, y='a')assert m.model_dump() == {'x': 1}


```

The [`extra`](https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict.extra) configuration value can be used to control this behavior:

```
from pydantic import BaseModel, ConfigDictclass Model(BaseModel):  x: int  model_config = ConfigDict(extra='allow')m = Model(x=1, y='a')  assert m.model_dump() == {'x': 1, 'y': 'a'}assert m.__pydantic_extra__ == {'y': 'a'}


```

If [`extra`](https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict.extra) was set to `'forbid'`, this would fail.
The configuration can take three values:
  * `'ignore'`: Providing extra data is ignored (the default).
  * `'forbid'`: Providing extra data is not permitted.
  * `'allow'`: Providing extra data is allowed and stored in the `__pydantic_extra__` dictionary attribute. The `__pydantic_extra__` can explicitly be annotated to provide validation for extra fields.


The validation methods (e.g. [`model_validate()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_validate)) have an optional `extra` argument that will override the `extra` configuration value of the model for that validation call.
For more details, refer to the [`extra`](https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict.extra) API documentation.
Pydantic dataclasses also support extra data (see the [dataclass configuration](https://pydantic.dev/docs/validation/latest/concepts/dataclasses#dataclass-config) section).
## Nested models
[](https://pydantic.dev/docs/validation/latest/concepts/models/#nested-models)
More complex hierarchical data structures can be defined using models themselves as types in annotations.

```
from typing import Optionalfrom pydantic import BaseModelclass Foo(BaseModel):    count: int    size: Optional[float] = Noneclass Bar(BaseModel):    apple: str = 'x'    banana: str = 'y'class Spam(BaseModel):    foo: Foo    bars: list[Bar]m = Spam(foo={'count': 4}, bars=[{'apple': 'x1'}, {'apple': 'x2'}])print(m)"""foo=Foo(count=4, size=None) bars=[Bar(apple='x1', banana='y'), Bar(apple='x2', banana='y')]"""print(m.model_dump())"""{    'foo': {'count': 4, 'size': None},    'bars': [{'apple': 'x1', 'banana': 'y'}, {'apple': 'x2', 'banana': 'y'}],}"""


```

Self-referencing models are supported. For more details, see the documentation related to [forward annotations](https://pydantic.dev/docs/validation/latest/concepts/forward_annotations#self-referencing-or-recursive-models).
## Rebuilding model schema
[](https://pydantic.dev/docs/validation/latest/concepts/models/#rebuilding-model-schema)
When you define a model class in your code, Pydantic will analyze the body of the class to collect a variety of information required to perform validation and serialization, gathered in a core schema. Notably, the model’s type annotations are evaluated to understand the valid types for each field (more information can be found in the [Architecture](https://pydantic.dev/docs/validation/latest/internals/architecture) documentation). However, it might be the case that annotations refer to symbols not defined when the model class is being created. To circumvent this issue, the [`model_rebuild()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_rebuild) method can be used:

```
from pydantic import BaseModel, PydanticUserErrorclass Foo(BaseModel):  x: 'Bar'  try:  Foo.model_json_schema()except PydanticUserError as e:  print(e)  """  `Foo` is not fully defined; you should define `Bar`, then call `Foo.model_rebuild()`.  For further information visit https://errors.pydantic.dev/2/u/class-not-fully-defined  """class Bar(BaseModel):  passFoo.model_rebuild()print(Foo.model_json_schema())"""{  '$defs': {'Bar': {'properties': {}, 'title': 'Bar', 'type': 'object'}},  'properties': {'x': {'$ref': '#/$defs/Bar'}},  'required': ['x'],  'title': 'Foo',  'type': 'object',}"""


```

`Bar` is not yet defined when the `Foo` class is being created. For this reason, a [forward annotation](https://pydantic.dev/docs/validation/latest/concepts/forward_annotations) is being used.
Pydantic tries to determine when this is necessary automatically and error if it wasn’t done, but you may want to call [`model_rebuild()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_rebuild) proactively when dealing with recursive models or generics.
In V2, [`model_rebuild()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_rebuild) replaced `update_forward_refs()` from V1. There are some slight differences with the new behavior. The biggest change is that when calling [`model_rebuild()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_rebuild) on the outermost model, it builds a core schema used for validation of the whole model (nested models and all), so all types at all levels need to be ready before [`model_rebuild()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_rebuild) is called.
## Validating data
[](https://pydantic.dev/docs/validation/latest/concepts/models/#validating-data)
Pydantic can validate data in three different modes: _Python_ , _JSON_ and _strings_.
The _Python_ mode gets used when using:
  * The `__init__()` model constructor. Field values must be provided using keyword arguments.
  * [`model_validate()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_validate): data can be provided either as a dictionary, or as a model instance (by default, instances are assumed to be valid; see the [`revalidate_instances`](https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict.revalidate_instances) setting). [Arbitrary objects](https://pydantic.dev/docs/validation/latest/concepts/models/#arbitrary-class-instances) can also be provided if explicitly enabled.


The _JSON_ and _strings_ modes can be used with dedicated methods:
  * [`model_validate_json()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_validate_json): data is validated as a JSON string or `bytes` object. If your incoming data is a JSON payload, this is generally considered faster (instead of manually parsing the data as a dictionary). Learn more about JSON parsing in the [JSON](https://pydantic.dev/docs/validation/latest/concepts/json) documentation.
  * [`model_validate_strings()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_validate_strings): data is validated as a dictionary (can be nested) with string keys and values and validates the data in JSON mode so that said strings can be coerced into the correct types.


Compared to using the model constructor, it is possible to control several validation parameters when using the `model_validate_*()` methods ([strictness](https://pydantic.dev/docs/validation/latest/concepts/strict_mode), [extra data](https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data), [validation context](https://pydantic.dev/docs/validation/latest/concepts/validators#validation-context), etc.).
Depending on the types and model configuration involved, the _Python_ and _JSON_ modes may have different validation behavior (e.g. with [strictness](https://pydantic.dev/docs/validation/latest/concepts/strict_mode)). If you have data coming from a non-JSON source, but want the same validation behavior and errors you’d get from the _JSON_ mode, our recommendation for now is to either dump your data to JSON (e.g. using [`json.dumps()`](https://docs.python.org/3/library/json.html#json.dumps)), or use [`model_validate_strings()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_validate_strings) if the data takes the form of a (potentially nested) dictionary with string keys and values. Progress for this feature can be tracked in [this issue](https://github.com/pydantic/pydantic/issues/11154).

```
from datetime import datetimefrom typing import Optionalfrom pydantic import BaseModel, ValidationErrorclass User(BaseModel):    id: int    name: str = 'John Doe'    signup_ts: Optional[datetime] = Nonem = User.model_validate({'id': 123, 'name': 'James'})print(m)#> id=123 name='James' signup_ts=Nonetry:    m = User.model_validate_json('{"id": 123, "name": 123}')except ValidationError as e:    print(e)    """    1 validation error for User    name      Input should be a valid string [type=string_type, input_value=123, input_type=int]    """m = User.model_validate_strings({'id': '123', 'name': 'James'})print(m)#> id=123 name='James' signup_ts=Nonem = User.model_validate_strings(    {'id': '123', 'name': 'James', 'signup_ts': '2024-04-01T12:00:00'})print(m)#> id=123 name='James' signup_ts=datetime.datetime(2024, 4, 1, 12, 0)try:    m = User.model_validate_strings(        {'id': '123', 'name': 'James', 'signup_ts': '2024-04-01'}, strict=True    )except ValidationError as e:    print(e)    """    1 validation error for User    signup_ts      Input should be a valid datetime, invalid datetime separator, expected `T`, `t`, `_` or space [type=datetime_parsing, input_value='2024-04-01', input_type=str]    """


```

### Creating models without validation
[](https://pydantic.dev/docs/validation/latest/concepts/models/#creating-models-without-validation)
Pydantic also provides the [`model_construct()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_construct) method, which allows models to be created **without validation**. This can be useful in at least a few cases:
  * when working with complex data that is already known to be valid (for performance reasons)
  * when one or more of the validator functions are non-idempotent
  * when one or more of the validator functions have side effects that you don’t want to be triggered.


[`model_construct()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_construct) does not do any validation, meaning it can create models which are invalid. **You should only ever use the[`model_construct()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_construct) method with data which has already been validated, or that you definitely trust.**
In Pydantic V2, the performance gap between validation (either with direct instantiation or the `model_validate*` methods) and [`model_construct()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_construct) has been narrowed considerably. For simple models, going with validation may even be faster. If you are using [`model_construct()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_construct) for performance reasons, you may want to profile your use case before assuming it is actually faster.
Note that for [root models](https://pydantic.dev/docs/validation/latest/concepts/models/#rootmodel-and-custom-root-types), the root value can be passed to [`model_construct()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_construct) positionally, instead of using a keyword argument.
Here are some additional notes on the behavior of [`model_construct()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_construct):
  * When we say “no validation is performed” — this includes converting dictionaries to model instances. So if you have a field referring to a model type, you will need to convert the inner dictionary to a model yourself.
  * If you do not pass keyword arguments for fields with defaults, the default values will still be used.
  * For models with private attributes, the `__pydantic_private__` dictionary will be populated the same as it would be when creating the model with validation.
  * No `__init__` method from the model or any of its parent classes will be called, even when a custom `__init__` method is defined.


[extra data](https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data) behavior with [`model_construct()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_construct)
  * For models with [`extra`](https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict.extra) set to `'allow'`, data not corresponding to fields will be correctly stored in the `__pydantic_extra__` dictionary and saved to the model’s `__dict__` attribute.
  * For models with [`extra`](https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict.extra) set to `'ignore'`, data not corresponding to fields will be ignored — that is, not stored in `__pydantic_extra__` or `__dict__` on the instance.
  * Unlike when instantiating the model with validation, a call to [`model_construct()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_construct) with [`extra`](https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict.extra) set to `'forbid'` doesn’t raise an error in the presence of data not corresponding to fields. Rather, said input data is simply ignored.


### Defining a custom `__init__()`
[](https://pydantic.dev/docs/validation/latest/concepts/models/#defining-a-custom-__init__)
Pydantic provides a default `__init__()` implementation for Pydantic models, that is called _only_ when using the model constructor (and not with the `model_validate_*()` methods). This implementation delegates validation to `pydantic-core`.
However, it is possible to define a custom `__init__()` on your models. In this case, it will be called unconditionally from all the [validation methods](https://pydantic.dev/docs/validation/latest/concepts/models/#validating-data), without performing validation (and so you should call `super().__init__(**kwargs)` in your implementation).
Defining a custom `__init__()` is not recommended, as all the validation parameters ([strictness](https://pydantic.dev/docs/validation/latest/concepts/strict_mode), [extra data behavior](https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data), [validation context](https://pydantic.dev/docs/validation/latest/concepts/validators#validation-context)) will be lost. If you need to perform actions after the model was initialized, you can make use of _after_ [field](https://pydantic.dev/docs/validation/latest/concepts/validators#field-after-validator) or [model](https://pydantic.dev/docs/validation/latest/concepts/validators#model-after-validator) validators, or define a [`model_post_init()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_post_init) implementation:

```
import loggingfrom typing import Anyfrom pydantic import BaseModelclass MyModel(BaseModel):    id: int    def model_post_init(self, context: Any) -> None:        logging.info("Model initialized with id %d", self.id)


```

## Error handling
[](https://pydantic.dev/docs/validation/latest/concepts/models/#error-handling)
Pydantic will raise a [`ValidationError`](https://pydantic.dev/docs/validation/latest/api/pydantic-core/pydantic_core/#pydantic_core.ValidationError) exception whenever it finds an error in the data it’s validating.
A single exception will be raised regardless of the number of errors found, and that validation error will contain information about all of the errors and how they happened.
See [Error Handling](https://pydantic.dev/docs/validation/latest/errors/errors) for details on standard and custom errors.
As a demonstration:

```
from pydantic import BaseModel, ValidationErrorclass Model(BaseModel):    list_of_ints: list[int]    a_float: floatdata = {    'list_of_ints': ['1', 2, 'bad'],    'a_float': 'not a float',}try:    Model(**data)except ValidationError as e:    print(e)    """    2 validation errors for Model    list_of_ints.2      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='bad', input_type=str]    a_float      Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='not a float', input_type=str]    """


```

## Arbitrary class instances
[](https://pydantic.dev/docs/validation/latest/concepts/models/#arbitrary-class-instances)
(Formerly known as “ORM Mode”/`from_orm()`).
When using the [`model_validate()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_validate) method, Pydantic can also validate arbitrary objects, by getting attributes on the object corresponding the field names. One common application of this functionality is integration with object-relational mappings (ORMs).
This feature need to be manually enabled, either by setting the [`from_attributes`](https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict.from_attributes) configuration value, or by using the `from_attributes` parameter on [`model_validate()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_validate).
The example here uses [SQLAlchemy](https://www.sqlalchemy.org/), but the same approach should work for any ORM.

```
from typing import Annotatedfrom sqlalchemy import ARRAY, Stringfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_columnfrom pydantic import BaseModel, ConfigDict, StringConstraintsclass Base(DeclarativeBase):    passclass CompanyOrm(Base):    __tablename__ = 'companies'    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)    public_key: Mapped[str] = mapped_column(        String(20), index=True, nullable=False, unique=True    )    domains: Mapped[list[str]] = mapped_column(ARRAY(String(255)))class CompanyModel(BaseModel):    model_config = ConfigDict(from_attributes=True)    id: int    public_key: Annotated[str, StringConstraints(max_length=20)]    domains: list[Annotated[str, StringConstraints(max_length=255)]]co_orm = CompanyOrm(    id=123,    public_key='foobar',    domains=['example.com', 'foobar.com'],)print(co_orm)#> <__main__.CompanyOrm object at 0x0123456789ab>co_model = CompanyModel.model_validate(co_orm)print(co_model)#> id=123 public_key='foobar' domains=['example.com', 'foobar.com']


```

### Nested attributes
[](https://pydantic.dev/docs/validation/latest/concepts/models/#nested-attributes)
When using attributes to validate models, model instances will be created from both top-level attributes and deeper-nested attributes as appropriate.
Here is an example demonstrating the principle:

```
from pydantic import BaseModel, ConfigDictclass PetCls:    def __init__(self, *, name: str) -> None:        self.name = nameclass PersonCls:    def __init__(self, *, name: str, pets: list[PetCls]) -> None:        self.name = name        self.pets = petsclass Pet(BaseModel):    model_config = ConfigDict(from_attributes=True)    name: strclass Person(BaseModel):    model_config = ConfigDict(from_attributes=True)    name: str    pets: list[Pet]bones = PetCls(name='Bones')orion = PetCls(name='Orion')anna = PersonCls(name='Anna', pets=[bones, orion])anna_model = Person.model_validate(anna)print(anna_model)#> name='Anna' pets=[Pet(name='Bones'), Pet(name='Orion')]


```

## Model copy
[](https://pydantic.dev/docs/validation/latest/concepts/models/#model-copy)
API Documentation
[`pydantic.main.BaseModel.model_copy`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_copy)

The [`model_copy()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_copy) method allows models to be duplicated (with optional updates), which is particularly useful when working with frozen models.

```
from pydantic import BaseModelclass BarModel(BaseModel):    whatever: intclass FooBarModel(BaseModel):    banana: float    foo: str    bar: BarModelm = FooBarModel(banana=3.14, foo='hello', bar={'whatever': 123})print(m.model_copy(update={'banana': 0}))#> banana=0 foo='hello' bar=BarModel(whatever=123)# normal copy gives the same object reference for bar:print(id(m.bar) == id(m.model_copy().bar))#> True# deep copy gives a new object reference for `bar`:print(id(m.bar) == id(m.model_copy(deep=True).bar))#> False


```

## Generic models
[](https://pydantic.dev/docs/validation/latest/concepts/models/#generic-models)
Pydantic supports the creation of generic models to make it easier to reuse a common model structure. Both the new [type parameter syntax](https://docs.python.org/3/reference/compound_stmts.html#type-params) (introduced by [PEP 695](https://peps.python.org/pep-0695/) in Python 3.12) and the old syntax are supported (refer to [the Python documentation](https://docs.python.org/3/library/typing.html#building-generic-types-and-type-aliases) for more details).
Here is an example using a generic Pydantic model to create an easily-reused HTTP response payload wrapper:
  * [ Python 3.9 and above ](https://pydantic.dev/docs/validation/latest/concepts/models/#tab-panel-491)
  * [ Python 3.12 and above (new syntax) ](https://pydantic.dev/docs/validation/latest/concepts/models/#tab-panel-492)


```
from typing import Generic, TypeVarfrom pydantic import BaseModel, ValidationErrorDataT = TypeVar('DataT')  class DataModel(BaseModel):  number: intclass Response(BaseModel, Generic[DataT]):    data: DataT  print(Response[int](data=1))#> data=1print(Response[str](data='value'))#> data='value'print(Response[str](data='value').model_dump())#> {'data': 'value'}data = DataModel(number=1)print(Response[DataModel](data=data).model_dump())#> {'data': {'number': 1}}try:  Response[int](data='value')except ValidationError as e:  print(e)  """  1 validation error for Response[int]  data    Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='value', input_type=str]  """


```

Declare one or more [type variables](https://docs.python.org/3/library/typing.html#typing.TypeVar) to use to parameterize your model.
Declare a Pydantic model that inherits from [`BaseModel`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel) and [`typing.Generic`](https://docs.python.org/3/library/typing.html#typing.Generic) (in this specific order), and add the list of type variables you declared previously as parameters to the [`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic) parent.
Use the type variables as annotations where you will want to replace them with other types.

```
from pydantic import BaseModel, ValidationErrorclass DataModel(BaseModel):  number: intclass Response[DataT](BaseModel):    data: DataT  print(Response[int](data=1))#> data=1print(Response[str](data='value'))#> data='value'print(Response[str](data='value').model_dump())#> {'data': 'value'}data = DataModel(number=1)print(Response[DataModel](data=data).model_dump())#> {'data': {'number': 1}}try:  Response[int](data='value')except ValidationError as e:  print(e)  """  1 validation error for Response[int]  data    Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='value', input_type=str]  """


```

Declare a Pydantic model and add the list of type variables as type parameters.
Use the type variables as annotations where you will want to replace them with other types.
✦ New in v2.11
Full support for the [type parameter syntax](https://docs.python.org/3/reference/compound_stmts.html#type-params) and [type variable defaults](https://typing.python.org/en/latest/spec/generics.html#type-parameter-defaults).
When parametrizing a model with a concrete type, Pydantic **does not** validate that the provided type is [assignable to the type variable](https://typing.readthedocs.io/en/latest/spec/generics.html#type-variables-with-an-upper-bound) if it has an upper bound.
Any [configuration](https://pydantic.dev/docs/validation/latest/concepts/config), [validation](https://pydantic.dev/docs/validation/latest/concepts/validators) or [serialization](https://pydantic.dev/docs/validation/latest/concepts/serialization) logic set on the generic model will also be applied to the parametrized classes, in the same way as when inheriting from a model class. Any custom methods or attributes will also be inherited.
Generic models also integrate properly with type checkers, so you get all the type checking you would expect if you were to declare a distinct type for each parametrization.
Internally, Pydantic creates subclasses of the generic model at runtime when the generic model class is parametrized. These classes are cached, so there should be minimal overhead introduced by the use of generics models.
To inherit from a generic model and preserve the fact that it is generic, the subclass must also inherit from [`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic):

```
from typing import Generic, TypeVarfrom pydantic import BaseModelTypeX = TypeVar('TypeX')class BaseClass(BaseModel, Generic[TypeX]):    X: TypeXclass ChildClass(BaseClass[TypeX], Generic[TypeX]):    pass# Parametrize `TypeX` with `int`:print(ChildClass[int](X=1))#> X=1


```

You can also create a generic subclass of a model that partially or fully replaces the type variables in the superclass:

```
from typing import Generic, TypeVarfrom pydantic import BaseModelTypeX = TypeVar('TypeX')TypeY = TypeVar('TypeY')TypeZ = TypeVar('TypeZ')class BaseClass(BaseModel, Generic[TypeX, TypeY]):    x: TypeX    y: TypeYclass ChildClass(BaseClass[int, TypeY], Generic[TypeY, TypeZ]):    z: TypeZ# Parametrize `TypeY` with `str`:print(ChildClass[str, int](x='1', y='y', z='3'))#> x=1 y='y' z=3


```

If the name of the concrete subclasses is important, you can also override the default name generation by overriding the [`model_parametrized_name()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_parametrized_name) method:

```
from typing import Any, Generic, TypeVarfrom pydantic import BaseModelDataT = TypeVar('DataT')class Response(BaseModel, Generic[DataT]):    data: DataT    @classmethod    def model_parametrized_name(cls, params: tuple[type[Any], ...]) -> str:        return f'{params[0].__name__.title()}Response'print(repr(Response[int](data=1)))#> IntResponse(data=1)print(repr(Response[str](data='a')))#> StrResponse(data='a')


```

You can use parametrized generic models as types in other models:

```
from typing import Generic, TypeVarfrom pydantic import BaseModelT = TypeVar('T')class ResponseModel(BaseModel, Generic[T]):    content: Tclass Product(BaseModel):    name: str    price: floatclass Order(BaseModel):    id: int    product: ResponseModel[Product]product = Product(name='Apple', price=0.5)response = ResponseModel[Product](content=product)order = Order(id=1, product=response)print(repr(order))"""Order(id=1, product=ResponseModel[Product](content=Product(name='Apple', price=0.5)))"""


```

Using the same type variable in nested models allows you to enforce typing relationships at different points in your model:

```
from typing import Generic, TypeVarfrom pydantic import BaseModel, ValidationErrorT = TypeVar('T')class InnerT(BaseModel, Generic[T]):  inner: Tclass OuterT(BaseModel, Generic[T]):  outer: T  nested: InnerT[T]nested = InnerT[int](inner=1)print(OuterT[int](outer=1, nested=nested))#> outer=1 nested=InnerT[int](inner=1)try:  print(OuterT[int](outer='a', nested=InnerT(inner='a')))  except ValidationError as e:  print(e)  """  2 validation errors for OuterT[int]  outer    Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]  nested.inner    Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]  """


```

The `OuterT` model is parametrized with `int`, but the data associated with the `T` annotations during validation is of type `str`, leading to validation errors.
While it may not raise an error, we strongly advise against using parametrized generics in [`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance) checks.
For example, you should not do `isinstance(my_model, MyGenericModel[int])`. However, it is fine to do `isinstance(my_model, MyGenericModel)` (note that, for standard generics, it would raise an error to do a subclass check with a parameterized generic class).
If you need to perform [`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance) checks against parametrized generics, you can do this by subclassing the parametrized generic class:

```
class MyIntModel(MyGenericModel[int]): ...isinstance(my_model, MyIntModel)


```

Implementation Details
When using nested generic models, Pydantic sometimes performs revalidation in an attempt to produce the most intuitive validation result. Specifically, if you have a field of type `GenericModel[SomeType]` and you validate data like `GenericModel[SomeCompatibleType]` against this field, we will inspect the data, recognize that the input data is sort of a “loose” subclass of `GenericModel`, and revalidate the contained `SomeCompatibleType` data.
This adds some validation overhead, but makes things more intuitive for cases like that shown below.

```
from typing import Any, Generic, TypeVarfrom pydantic import BaseModelT = TypeVar('T')class GenericModel(BaseModel, Generic[T]):    a: Tclass Model(BaseModel):    inner: GenericModel[Any]print(repr(Model.model_validate(Model(inner=GenericModel[int](a=1)))))#> Model(inner=GenericModel[Any](a=1))


```

Note, validation will still fail if you, for example are validating against `GenericModel[int]` and pass in an instance `GenericModel[str](a='not an int')`.
It’s also worth noting that this pattern will re-trigger any custom validation as well, like additional model validators and the like. Validators will be called once on the first pass, validating directly against `GenericModel[Any]`. That validation fails, as `GenericModel[int]` is not a subclass of `GenericModel[Any]`. This relates to the warning above about the complications of using parametrized generics in `isinstance()` and `issubclass()` checks. Then, the validators will be called again on the second pass, during more lax force-revalidation phase, which succeeds. To better understand this consequence, see below:

```
from typing import Any, Generic, Self, TypeVarfrom pydantic import BaseModel, model_validatorT = TypeVar('T')class GenericModel(BaseModel, Generic[T]):    a: T    @model_validator(mode='after')    def validate_after(self: Self) -> Self:        print('after validator running custom validation...')        return selfclass Model(BaseModel):    inner: GenericModel[Any]m = Model.model_validate(Model(inner=GenericModel[int](a=1)))#> after validator running custom validation...#> after validator running custom validation...print(repr(m))#> Model(inner=GenericModel[Any](a=1))


```

### Validation of unparametrized type variables
[](https://pydantic.dev/docs/validation/latest/concepts/models/#validation-of-unparametrized-type-variables)
When leaving type variables unparametrized, Pydantic treats generic models similarly to how it treats built-in generic types like [`list`](https://docs.python.org/3/glossary.html#term-list) and [`dict`](https://docs.python.org/3/reference/expressions.html#dict):
  * If the type variable is [bound](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-upper-bounds) or [constrained](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-constraints) to a specific type, it will be used.
  * If the type variable has a default type (as specified by [PEP 696](https://peps.python.org/pep-0696/)), it will be used.
  * For unbound or unconstrained type variables, Pydantic will fallback to [`Any`](https://docs.python.org/3/library/typing.html#typing.Any).


```
from typing import Genericfrom typing_extensions import TypeVarfrom pydantic import BaseModel, ValidationErrorT = TypeVar('T')U = TypeVar('U', bound=int)V = TypeVar('V', default=str)class Model(BaseModel, Generic[T, U, V]):    t: T    u: U    v: Vprint(Model(t='t', u=1, v='v'))#> t='t' u=1 v='v'try:    Model(t='t', u='u', v=1)except ValidationError as exc:    print(exc)    """    2 validation errors for Model    u      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='u', input_type=str]    v      Input should be a valid string [type=string_type, input_value=1, input_type=int]    """


```

In some cases, validation against an unparametrized generic model can lead to data loss. Specifically, if a subtype of the type variable upper bound, constraints, or default is being used and the model isn’t explicitly parametrized, the resulting type **will not be** the one being provided:

```
from typing import Generic, TypeVarfrom pydantic import BaseModelItemT = TypeVar('ItemT', bound='ItemBase')class ItemBase(BaseModel): ...class IntItem(ItemBase):  value: intclass ItemHolder(BaseModel, Generic[ItemT]):  item: ItemTloaded_data = {'item': {'value': 1}}print(ItemHolder(**loaded_data))  #> item=ItemBase()print(ItemHolder[IntItem](**loaded_data))  #> item=IntItem(value=1)


```

When the generic isn't parametrized, the input data is validated against the `ItemT` upper bound. Given that `ItemBase` has no fields, the `item` field information is lost.
In this case, the type variable is explicitly parametrized, so the input data is validated against the `IntItem` class.
### Serialization of unparametrized type variables
[](https://pydantic.dev/docs/validation/latest/concepts/models/#serialization-of-unparametrized-type-variables)
The behavior of serialization differs when using type variables with [upper bounds](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-upper-bounds), [constraints](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-constraints), or a default value:
If a Pydantic model is used in a type variable upper bound and the type variable is never parametrized, then Pydantic will use the upper bound for validation but treat the value as [`Any`](https://docs.python.org/3/library/typing.html#typing.Any) in terms of serialization:

```
from typing import Generic, TypeVarfrom pydantic import BaseModelclass ErrorDetails(BaseModel):    foo: strErrorDataT = TypeVar('ErrorDataT', bound=ErrorDetails)class Error(BaseModel, Generic[ErrorDataT]):    message: str    details: ErrorDataTclass MyErrorDetails(ErrorDetails):    bar: str# serialized as Anyerror = Error(    message='We just had an error',    details=MyErrorDetails(foo='var', bar='var2'),)assert error.model_dump() == {    'message': 'We just had an error',    'details': {        'foo': 'var',        'bar': 'var2',    },}# serialized using the concrete parametrization# note that `'bar': 'var2'` is missingerror = Error[ErrorDetails](    message='We just had an error',    details=ErrorDetails(foo='var'),)assert error.model_dump() == {    'message': 'We just had an error',    'details': {        'foo': 'var',    },}


```

Here’s another example of the above behavior, enumerating all permutations regarding bound specification and generic type parametrization:

```
from typing import Generic, TypeVarfrom pydantic import BaseModelTBound = TypeVar('TBound', bound=BaseModel)TNoBound = TypeVar('TNoBound')class IntValue(BaseModel):    value: intclass ItemBound(BaseModel, Generic[TBound]):    item: TBoundclass ItemNoBound(BaseModel, Generic[TNoBound]):    item: TNoBounditem_bound_inferred = ItemBound(item=IntValue(value=3))item_bound_explicit = ItemBound[IntValue](item=IntValue(value=3))item_no_bound_inferred = ItemNoBound(item=IntValue(value=3))item_no_bound_explicit = ItemNoBound[IntValue](item=IntValue(value=3))# calling `print(x.model_dump())` on any of the above instances results in the following:#> {'item': {'value': 3}}


```

However, if [constraints](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-constraints) or a default value (as per [PEP 696](https://peps.python.org/pep-0696/)) is being used, then the default type or constraints will be used for both validation and serialization if the type variable is not parametrized. You can override this behavior using [`SerializeAsAny`](https://pydantic.dev/docs/validation/latest/concepts/serialization#serializeasany-annotation):

```
from typing import Genericfrom typing_extensions import TypeVarfrom pydantic import BaseModel, SerializeAsAnyclass ErrorDetails(BaseModel):    foo: strErrorDataT = TypeVar('ErrorDataT', default=ErrorDetails)class Error(BaseModel, Generic[ErrorDataT]):    message: str    details: ErrorDataTclass MyErrorDetails(ErrorDetails):    bar: str# serialized using the default's serializererror = Error(    message='We just had an error',    details=MyErrorDetails(foo='var', bar='var2'),)assert error.model_dump() == {    'message': 'We just had an error',    'details': {        'foo': 'var',    },}# If `ErrorDataT` was using an upper bound, `bar` would be present in `details`.class SerializeAsAnyError(BaseModel, Generic[ErrorDataT]):    message: str    details: SerializeAsAny[ErrorDataT]# serialized as Anyerror = SerializeAsAnyError(    message='We just had an error',    details=MyErrorDetails(foo='var', bar='baz'),)assert error.model_dump() == {    'message': 'We just had an error',    'details': {        'foo': 'var',        'bar': 'baz',    },}


```

## Dynamic model creation
[](https://pydantic.dev/docs/validation/latest/concepts/models/#dynamic-model-creation)
API Documentation
[`pydantic.main.create_model`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.create_model)

There are some occasions where it is desirable to create a model using runtime information to specify the fields. Pydantic provides the [`create_model()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.create_model) function to allow models to be created dynamically:

```
from pydantic import BaseModel, create_modelDynamicFoobarModel = create_model('DynamicFoobarModel', foo=str, bar=(int, 123))# Equivalent to:class StaticFoobarModel(BaseModel):    foo: str    bar: int = 123


```

Field definitions are specified as keyword arguments, and should either be:
  * A single element, representing the type annotation of the field.
  * A two-tuple, the first element being the type and the second element the assigned value (either a default or the [`Field()`](https://pydantic.dev/docs/validation/latest/api/pydantic/fields/#pydantic.fields.Field) function).


↻ Changed in v2.11
When providing a single element for field definitions, any type can be used (previously, only an [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated) form could be provided).
Here is a more advanced example:

```
from typing import Annotatedfrom pydantic import BaseModel, Field, PrivateAttr, create_modelDynamicModel = create_model(    'DynamicModel',    foo=(str, Field(alias='FOO')),    bar=Annotated[str, Field(description='Bar field')],    _private=(int, PrivateAttr(default=1)),)class StaticModel(BaseModel):    foo: str = Field(alias='FOO')    bar: Annotated[str, Field(description='Bar field')]    _private: int = PrivateAttr(default=1)


```

The special keyword arguments `__config__` and `__base__` can be used to customize the new model. This includes extending a base model with extra fields.

```
from pydantic import BaseModel, create_modelclass FooModel(BaseModel):    foo: str    bar: int = 123BarModel = create_model(    'BarModel',    apple=(str, 'russet'),    banana=(str, 'yellow'),    __base__=FooModel,)print(BarModel)#> <class '__main__.BarModel'>print(BarModel.model_fields.keys())#> dict_keys(['foo', 'bar', 'apple', 'banana'])


```

You can also add validators by passing a dictionary to the `__validators__` argument.

```
from pydantic import ValidationError, create_model, field_validatordef alphanum(cls, v):  assert v.isalnum(), 'must be alphanumeric'  return vvalidators = {  'username_validator': field_validator('username')(alphanum)  }UserModel = create_model(  'UserModel', username=(str, ...), __validators__=validators)user = UserModel(username='scolvin')print(user)#> username='scolvin'try:  UserModel(username='scolvi%n')except ValidationError as e:  print(e)  """  1 validation error for UserModel  username    Assertion failed, must be alphanumeric [type=assertion_error, input_value='scolvi%n', input_type=str]  """


```

Make sure that the validators names do not clash with any of the field names as internally, Pydantic gathers all members into a namespace and mimics the normal creation of a class using the [`types` module utilities](https://docs.python.org/3/library/types.html#dynamic-type-creation).
To pickle a dynamically created model:
  * the model must be defined globally
  * the `__module__` argument must be provided


This function may execute arbitrary code contained in field annotations, if string references need to be evaluated.
See [Security implications of introspecting annotations](https://docs.python.org/3/library/annotationlib.html#annotationlib-security) for more information.
See also: the [dynamic model example](https://pydantic.dev/docs/validation/latest/examples/dynamic_models), providing guidelines to derive an optional model from another one.
##  `RootModel` and custom root types
[](https://pydantic.dev/docs/validation/latest/concepts/models/#rootmodel-and-custom-root-types)
API Documentation
[`pydantic.root_model.RootModel`](https://pydantic.dev/docs/validation/latest/api/pydantic/root_model/#pydantic.root_model.RootModel)

Pydantic models can be defined with a “custom root type” by subclassing [`pydantic.RootModel`](https://pydantic.dev/docs/validation/latest/api/pydantic/root_model/#pydantic.root_model.RootModel).
The root type can be any type supported by Pydantic, and is specified by the generic parameter to `RootModel`. The root value can be passed to the model `__init__` or [`model_validate`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_validate) via the first and only argument.
Here’s an example of how this works:

```
from pydantic import RootModelPets = RootModel[list[str]]PetsByName = RootModel[dict[str, str]]print(Pets(['dog', 'cat']))#> root=['dog', 'cat']print(Pets(['dog', 'cat']).model_dump_json())#> ["dog","cat"]print(Pets.model_validate(['dog', 'cat']))#> root=['dog', 'cat']print(Pets.model_json_schema())"""{'items': {'type': 'string'}, 'title': 'RootModel[list[str]]', 'type': 'array'}"""print(PetsByName({'Otis': 'dog', 'Milo': 'cat'}))#> root={'Otis': 'dog', 'Milo': 'cat'}print(PetsByName({'Otis': 'dog', 'Milo': 'cat'}).model_dump_json())#> {"Otis":"dog","Milo":"cat"}print(PetsByName.model_validate({'Otis': 'dog', 'Milo': 'cat'}))#> root={'Otis': 'dog', 'Milo': 'cat'}


```

If you want to access items in the `root` field directly or to iterate over the items, you can implement custom `__iter__` and `__getitem__` functions, as shown in the following example.

```
from pydantic import RootModelclass Pets(RootModel):    root: list[str]    def __iter__(self):        return iter(self.root)    def __getitem__(self, item):        return self.root[item]pets = Pets.model_validate(['dog', 'cat'])print(pets[0])#> dogprint([pet for pet in pets])#> ['dog', 'cat']


```

You can also create subclasses of the parametrized root model directly:

```
from pydantic import RootModelclass Pets(RootModel[list[str]]):    def describe(self) -> str:        return f'Pets: {", ".join(self.root)}'my_pets = Pets.model_validate(['dog', 'cat'])print(my_pets.describe())#> Pets: dog, cat


```

## Faux immutability
[](https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability)
Models can be configured to be immutable via `model_config['frozen'] = True`. When this is set, attempting to change the values of instance attributes will raise errors. See the [API reference](https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict.frozen) for more details.
This behavior was achieved in Pydantic V1 via the config setting `allow_mutation = False`. This config flag is deprecated in Pydantic V2, and has been replaced with `frozen`.
In Python, immutability is not enforced. Developers have the ability to modify objects that are conventionally considered “immutable” if they choose to do so.

```
from pydantic import BaseModel, ConfigDict, ValidationErrorclass FooBarModel(BaseModel):    model_config = ConfigDict(frozen=True)    a: str    b: dictfoobar = FooBarModel(a='hello', b={'apple': 'pear'})try:    foobar.a = 'different'except ValidationError as e:    print(e)    """    1 validation error for FooBarModel    a      Instance is frozen [type=frozen_instance, input_value='different', input_type=str]    """print(foobar.a)#> helloprint(foobar.b)#> {'apple': 'pear'}foobar.b['apple'] = 'grape'print(foobar.b)#> {'apple': 'grape'}


```

Trying to change `a` caused an error, and `a` remains unchanged. However, the dict `b` is mutable, and the immutability of `foobar` doesn’t stop `b` from being changed.
## Abstract base classes
[](https://pydantic.dev/docs/validation/latest/concepts/models/#abstract-base-classes)
Pydantic models can be used alongside Python’s [Abstract Base Classes](https://docs.python.org/3/library/abc.html) (ABCs).

```
import abcfrom pydantic import BaseModelclass FooBarModel(BaseModel, abc.ABC):    a: str    b: int    @abc.abstractmethod    def my_abstract_method(self):        pass


```

## Field ordering
[](https://pydantic.dev/docs/validation/latest/concepts/models/#field-ordering)
Field order affects models in the following ways:
  * field order is preserved in the model [JSON Schema](https://pydantic.dev/docs/validation/latest/concepts/json_schema)
  * field order is preserved in [validation errors](https://pydantic.dev/docs/validation/latest/concepts/models/#error-handling)
  * field order is preserved when [serializing data](https://pydantic.dev/docs/validation/latest/concepts/serialization#serializing-data)


```
from pydantic import BaseModel, ValidationErrorclass Model(BaseModel):    a: int    b: int = 2    c: int = 1    d: int = 0    e: floatprint(Model.model_fields.keys())#> dict_keys(['a', 'b', 'c', 'd', 'e'])m = Model(e=2, a=1)print(m.model_dump())#> {'a': 1, 'b': 2, 'c': 1, 'd': 0, 'e': 2.0}try:    Model(a='x', b='x', c='x', d='x', e='x')except ValidationError as err:    error_locations = [e['loc'] for e in err.errors()]print(error_locations)#> [('a',), ('b',), ('c',), ('d',), ('e',)]


```

## Automatically excluded attributes
[](https://pydantic.dev/docs/validation/latest/concepts/models/#automatically-excluded-attributes)
### Class variables
[](https://pydantic.dev/docs/validation/latest/concepts/models/#class-variables)
Attributes annotated with [`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar) are properly treated by Pydantic as class variables, and will not become fields on model instances:

```
from typing import ClassVarfrom pydantic import BaseModelclass Model(BaseModel):    x: ClassVar[int] = 1    y: int = 2m = Model()print(m)#> y=2print(Model.x)#> 1


```

### Private model attributes
[](https://pydantic.dev/docs/validation/latest/concepts/models/#private-model-attributes)
API Documentation
[`pydantic.fields.PrivateAttr`](https://pydantic.dev/docs/validation/latest/api/pydantic/fields/#pydantic.fields.PrivateAttr)

Attributes whose name has a leading underscore are not treated as fields by Pydantic, and are not included in the model schema. Instead, these are converted into a “private attribute” which is not validated or even set during calls to `__init__`, `model_validate`, etc.
Here is an example of usage:

```
from datetime import datetimefrom random import randintfrom typing import Anyfrom pydantic import BaseModel, PrivateAttrclass TimeAwareModel(BaseModel):    _processed_at: datetime = PrivateAttr(default_factory=datetime.now)    _secret_value: str    def model_post_init(self, context: Any) -> None:        # this could also be done with `default_factory`:        self._secret_value = randint(1, 5)m = TimeAwareModel()print(m._processed_at)#> 2032-01-02 03:04:05.000006print(m._secret_value)#> 3


```

Private attribute names must start with underscore to prevent conflicts with model fields. However, dunder names (such as `__attr__`) are not supported, and will be completely ignored from the model definition.
✦ New in v2.13
Default factories can take the validated model data as an argument.
## Model signature
[](https://pydantic.dev/docs/validation/latest/concepts/models/#model-signature)
All Pydantic models will have their signature generated based on their fields:

```
import inspectfrom pydantic import BaseModel, Fieldclass FooModel(BaseModel):    id: int    name: str = None    description: str = 'Foo'    apple: int = Field(alias='pear')print(inspect.signature(FooModel))#> (*, id: int, name: str = None, description: str = 'Foo', pear: int) -> None


```

An accurate signature is useful for introspection purposes and libraries like `FastAPI` or `hypothesis`.
The generated signature will also respect custom `__init__` functions:

```
import inspectfrom pydantic import BaseModelclass MyModel(BaseModel):    id: int    info: str = 'Foo'    def __init__(self, id: int = 1, *, bar: str, **data) -> None:        """My custom init!"""        super().__init__(id=id, bar=bar, **data)print(inspect.signature(MyModel))#> (id: int = 1, *, bar: str, info: str = 'Foo') -> None


```

To be included in the signature, a field’s alias or name must be a valid Python identifier. Pydantic will prioritize a field’s alias over its name when generating the signature, but may use the field name if the alias is not a valid Python identifier.
If a field’s alias and name are _both_ not valid identifiers (which may be possible through exotic use of `create_model`), a `**data` argument will be added. In addition, the `**data` argument will always be present in the signature if `model_config['extra'] == 'allow'`.
## Structural pattern matching
[](https://pydantic.dev/docs/validation/latest/concepts/models/#structural-pattern-matching)
Pydantic supports structural pattern matching for models, as introduced by [PEP 636](https://peps.python.org/pep-0636/) in Python 3.10.

```
from pydantic import BaseModelclass Pet(BaseModel):    name: str    species: stra = Pet(name='Bones', species='dog')match a:    # match `species` to 'dog', declare and initialize `dog_name`    case Pet(species='dog', name=dog_name):        print(f'{dog_name} is a dog')#> Bones is a dog    # default case    case _:        print('No dog matched')


```

A match-case statement may seem as if it creates a new model, but don’t be fooled; it is just syntactic sugar for getting an attribute and either comparing it or declaring and initializing it.
## Attribute copies
[](https://pydantic.dev/docs/validation/latest/concepts/models/#attribute-copies)
In many cases, arguments passed to the constructor will be copied in order to perform validation and, where necessary, coercion.
In this example, note that the ID of the list changes after the class is constructed because it has been copied during validation:

```
from pydantic import BaseModelclass C1:    arr = []    def __init__(self, in_arr):        self.arr = in_arrclass C2(BaseModel):    arr: list[int]arr_orig = [1, 9, 10, 3]c1 = C1(arr_orig)c2 = C2(arr=arr_orig)print(f'{id(c1.arr) == id(c2.arr)=}')#> id(c1.arr) == id(c2.arr)=False


```

There are some situations where Pydantic does not copy attributes, such as when passing models — we use the model as is. You can override this behaviour by setting [`model_config['revalidate_instances'] = 'always'`](https://pydantic.dev/docs/validation/latest/api/pydantic/config#pydantic.config.ConfigDict).
Was this page helpful? Thanks for your feedback!
[ Previous
Changelog ](https://pydantic.dev/docs/validation/latest/get-started/changelog/) [ Next
Fields ](https://pydantic.dev/docs/validation/latest/concepts/fields/)
© Pydantic Services Inc. 2025 to present
[ ](https://github.com/pydantic "Pydantic on GitHub") [ ](https://x.com/pydantic "Pydantic on X") [ ](https://www.linkedin.com/company/pydantic/ "Pydantic on LinkedIn") [ ](https://bsky.app/profile/pydantic.dev "Pydantic on Bluesky")


--- DOCUMENT: https://pydantic.dev/docs/validation/latest/get-started/ ---
# Welcome to Pydantic
[![CI](https://img.shields.io/github/actions/workflow/status/pydantic/pydantic/ci.yml?branch=main&logo=github&label=CI)](https://github.com/pydantic/pydantic/actions?query=event%3Apush+branch%3Amain+workflow%3ACI) [![Coverage](https://coverage-badge.samuelcolvin.workers.dev/pydantic/pydantic.svg)](https://github.com/pydantic/pydantic/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/pydantic.svg)](https://pypi.python.org/pypi/pydantic) [![CondaForge](https://img.shields.io/conda/v/conda-forge/pydantic.svg)](https://anaconda.org/conda-forge/pydantic) [![downloads](https://static.pepy.tech/badge/pydantic/month)](https://pepy.tech/project/pydantic)
[![license](https://img.shields.io/github/license/pydantic/pydantic.svg)](https://github.com/pydantic/pydantic/blob/main/LICENSE) [![llms.txt](https://img.shields.io/badge/llms.txt-green)](https://docs.pydantic.dev/latest/llms.txt)
Documentation for version: v2.13.3.
Pydantic is the most widely used data validation library for Python.
Fast and extensible, Pydantic plays nicely with your linters/IDE/brain. Define how data should be in pure, canonical Python 3.9+; validate it with Pydantic.
**[Pydantic Logfire](https://pydantic.dev/logfire)** is a production-grade observability platform for AI and general applications. See LLM interactions, agent behavior, API requests, and database queries in one unified trace. With SDKs for Python, JavaScript/TypeScript, and Rust, Logfire works with all OpenTelemetry-compatible languages.
Logfire integrates with many popular Python libraries including FastAPI, OpenAI and Pydantic itself, so you can use Logfire to monitor Pydantic validations and understand why some inputs fail validation:
Monitoring Pydantic with Logfire
```
from datetime import datetimeimport logfirefrom pydantic import BaseModellogfire.configure()logfire.instrument_pydantic()  class Delivery(BaseModel):  timestamp: datetime  dimensions: tuple[int, int]# this will record details of a successful validation to logfirem = Delivery(timestamp='2020-01-02T03:04:05Z', dimensions=['10', '20'])print(repr(m.timestamp))#> datetime.datetime(2020, 1, 2, 3, 4, 5, tzinfo=TzInfo(UTC))print(m.dimensions)#> (10, 20)Delivery(timestamp='2020-01-02T03:04:05Z', dimensions=['10'])


```

Set logfire record all both successful and failed validations, use `record='failure'` to only record failed validations, [learn more](https://logfire.pydantic.dev/docs/integrations/pydantic/).
This will raise a `ValidationError` since there are too few `dimensions`, details of the input data and validation errors will be recorded in Logfire.
Would give you a view like this in the Logfire platform:
[![Logfire Pydantic Integration](https://pydantic.dev/docs/validation/latest/img/logfire-pydantic-integration.png)](https://logfire.pydantic.dev/docs/guides/web-ui/live/)
This is just a toy example, but hopefully makes clear the potential value of instrumenting a more complex application.
**[Learn more about Pydantic Logfire](https://logfire.pydantic.dev/docs/)**
**Sign up for our newsletter,_The Pydantic Stack_ , with updates & tutorials on Pydantic, Logfire, and Pydantic AI:**
Subscribe
## Why use Pydantic?
[](https://pydantic.dev/docs/validation/latest/get-started/#why-use-pydantic)
  * **Powered by type hints** — with Pydantic, schema validation and serialization are controlled by type annotations; less to learn, less code to write, and integration with your IDE and static analysis tools. [Learn more…](https://pydantic.dev/docs/validation/latest/get-started/why#type-hints)
  * **Speed** — Pydantic’s core validation logic is written in Rust. As a result, Pydantic is among the fastest data validation libraries for Python. [Learn more…](https://pydantic.dev/docs/validation/latest/get-started/why#performance)
  * **JSON Schema** — Pydantic models can emit JSON Schema, allowing for easy integration with other tools. [Learn more…](https://pydantic.dev/docs/validation/latest/get-started/why#json-schema)
  * **Strict** and **Lax** mode — Pydantic can run in either strict mode (where data is not converted) or lax mode where Pydantic tries to coerce data to the correct type where appropriate. [Learn more…](https://pydantic.dev/docs/validation/latest/get-started/why#strict-lax)
  * **Dataclasses** , **TypedDicts** and more — Pydantic supports validation of many standard library types including `dataclass` and `TypedDict`. [Learn more…](https://pydantic.dev/docs/validation/latest/get-started/why#dataclasses-typeddict-more)
  * **Customisation** — Pydantic allows custom validators and serializers to alter how data is processed in many powerful ways. [Learn more…](https://pydantic.dev/docs/validation/latest/get-started/why#customisation)
  * **Ecosystem** — around 8,000 packages on PyPI use Pydantic, including massively popular libraries like _FastAPI_ , _huggingface_ , _Django Ninja_ , _SQLModel_ , & _LangChain_. [Learn more…](https://pydantic.dev/docs/validation/latest/get-started/why#ecosystem)
  * **Battle tested** — Pydantic is downloaded over 550M times/month and is used by all FAANG companies and 20 of the 25 largest companies on NASDAQ. If you’re trying to do something with Pydantic, someone else has probably already done it. [Learn more…](https://pydantic.dev/docs/validation/latest/get-started/why#using-pydantic)


[Installing Pydantic](https://pydantic.dev/docs/validation/latest/get-started/install) is as simple as: `pip install pydantic`
## Pydantic examples
[](https://pydantic.dev/docs/validation/latest/get-started/#pydantic-examples)
To see Pydantic at work, let’s start with a simple example, creating a custom class that inherits from `BaseModel`:
Validation Successful
```
from datetime import datetimefrom pydantic import BaseModel, PositiveIntclass User(BaseModel):  id: int    name: str = 'John Doe'    signup_ts: datetime | None    tastes: dict[str, PositiveInt]  external_data = {  'id': 123,  'signup_ts': '2019-06-01 12:22',    'tastes': {      'wine': 9,      b'cheese': 7,        'cabbage': '1',    },}user = User(**external_data)  print(user.id)  #> 123print(user.model_dump())  """{  'id': 123,  'name': 'John Doe',  'signup_ts': datetime.datetime(2019, 6, 1, 12, 22),  'tastes': {'wine': 9, 'cheese': 7, 'cabbage': 1},}"""


```

`id` is of type `int`; the annotation-only declaration tells Pydantic that this field is required. Strings, bytes, or floats will be coerced to integers if possible; otherwise an exception will be raised.
`name` is a string; because it has a default, it is not required.
`signup_ts` is a [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime) field that is required, but the value `None` may be provided; Pydantic will process either a [Unix timestamp](https://en.wikipedia.org/wiki/Unix_time) integer (e.g. `1496498400`) or a string representing the date and time.
`tastes` is a dictionary with string keys and positive integer values. The `PositiveInt` type is shorthand for `Annotated[int, annotated_types.Gt(0)]`.
The input here is an [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) formatted datetime, but Pydantic will convert it to a [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime) object.
The key here is `bytes`, but Pydantic will take care of coercing it to a string.
Similarly, Pydantic will coerce the string `'1'` to the integer `1`.
We create instance of `User` by passing our external data to `User` as keyword arguments.
We can access fields as attributes of the model.
We can convert the model to a dictionary with [`model_dump()`](https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/#pydantic.BaseModel.model_dump).
If validation fails, Pydantic will raise an error with a breakdown of what was wrong:
Validation Error
```
# continuing the above example...from datetime import datetimefrom pydantic import BaseModel, PositiveInt, ValidationErrorclass User(BaseModel):  id: int  name: str = 'John Doe'  signup_ts: datetime | None  tastes: dict[str, PositiveInt]external_data = {'id': 'not an int', 'tastes': {}}  try:  User(**external_data)  except ValidationError as e:  print(e.errors())  """  [      {          'type': 'int_parsing',          'loc': ('id',),          'msg': 'Input should be a valid integer, unable to parse string as an integer',          'input': 'not an int',          'url': 'https://errors.pydantic.dev/2/v/int_parsing',      },      {          'type': 'missing',          'loc': ('signup_ts',),          'msg': 'Field required',          'input': {'id': 'not an int', 'tastes': {}},          'url': 'https://errors.pydantic.dev/2/v/missing',      },  ]  """


```

The input data is wrong here — `id` is not a valid integer, and `signup_ts` is missing.
Trying to instantiate `User` will raise a [`ValidationError`](https://pydantic.dev/docs/validation/latest/api/pydantic-core/pydantic_core/#pydantic_core.ValidationError) with a list of errors.
## Who is using Pydantic?
[](https://pydantic.dev/docs/validation/latest/get-started/#who-is-using-pydantic)
Hundreds of organisations and packages are using Pydantic. Some of the prominent companies and organizations around the world who are using Pydantic include:
[![Adobe](https://pydantic.dev/docs/validation/logos/adobe_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-adobe "Adobe")
[![Amazon and AWS](https://pydantic.dev/docs/validation/logos/amazon_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-amazon "Amazon and AWS")
[![Anthropic](https://pydantic.dev/docs/validation/logos/anthropic_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-anthropic "Anthropic")
[![Apple](https://pydantic.dev/docs/validation/logos/apple_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-apple "Apple")
[![ASML](https://pydantic.dev/docs/validation/logos/asml_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-asml "ASML")
[![AstraZeneca](https://pydantic.dev/docs/validation/logos/astrazeneca_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-astrazeneca "AstraZeneca")
[![Cisco Systems](https://pydantic.dev/docs/validation/logos/cisco_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-cisco "Cisco Systems")
[![Capital One](https://pydantic.dev/docs/validation/logos/capital_one_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-capital_one "Capital One")
[![Comcast](https://pydantic.dev/docs/validation/logos/comcast_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-comcast "Comcast")
[![Datadog](https://pydantic.dev/docs/validation/logos/datadog_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-datadog "Datadog")
[![Facebook](https://pydantic.dev/docs/validation/logos/facebook_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-facebook "Facebook")
[![GitHub](https://pydantic.dev/docs/validation/logos/github_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-github "GitHub")
[![Google](https://pydantic.dev/docs/validation/logos/google_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-google "Google")
[![HSBC](https://pydantic.dev/docs/validation/logos/hsbc_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-hsbc "HSBC")
[![IBM](https://pydantic.dev/docs/validation/logos/ibm_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-ibm "IBM")
[![Intel](https://pydantic.dev/docs/validation/logos/intel_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-intel "Intel")
[![Intuit](https://pydantic.dev/docs/validation/logos/intuit_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-intuit "Intuit")
[![Intergovernmental Panel on Climate Change](https://pydantic.dev/docs/validation/logos/ipcc_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-ipcc "Intergovernmental Panel on Climate Change")
[![JPMorgan](https://pydantic.dev/docs/validation/logos/jpmorgan_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-jpmorgan "JPMorgan")
[![Jupyter](https://pydantic.dev/docs/validation/logos/jupyter_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-jupyter "Jupyter")
[![Microsoft](https://pydantic.dev/docs/validation/logos/microsoft_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-microsoft "Microsoft")
[![Molecular Science Software Institute](https://pydantic.dev/docs/validation/logos/molssi_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-molssi "Molecular Science Software Institute")
[![NASA](https://pydantic.dev/docs/validation/logos/nasa_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-nasa "NASA")
[![Netflix](https://pydantic.dev/docs/validation/logos/netflix_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-netflix "Netflix")
[![NSA](https://pydantic.dev/docs/validation/logos/nsa_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-nsa "NSA")
[![NVIDIA](https://pydantic.dev/docs/validation/logos/nvidia_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-nvidia "NVIDIA")
[![OpenAI](https://pydantic.dev/docs/validation/logos/openai_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-openai "OpenAI")
[![Oracle](https://pydantic.dev/docs/validation/logos/oracle_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-oracle "Oracle")
[![Palantir](https://pydantic.dev/docs/validation/logos/palantir_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-palantir "Palantir")
[![Qualcomm](https://pydantic.dev/docs/validation/logos/qualcomm_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-qualcomm "Qualcomm")
[![Red Hat](https://pydantic.dev/docs/validation/logos/redhat_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-redhat "Red Hat")
[![Revolut](https://pydantic.dev/docs/validation/logos/revolut_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-revolut "Revolut")
[![Robusta](https://pydantic.dev/docs/validation/logos/robusta_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-robusta "Robusta")
[![Salesforce](https://pydantic.dev/docs/validation/logos/salesforce_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-salesforce "Salesforce")
[![Starbucks](https://pydantic.dev/docs/validation/logos/starbucks_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-starbucks "Starbucks")
[![Texas Instruments](https://pydantic.dev/docs/validation/logos/ti_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-ti "Texas Instruments")
[![Twilio](https://pydantic.dev/docs/validation/logos/twilio_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-twilio "Twilio")
[![Twitter](https://pydantic.dev/docs/validation/logos/twitter_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-twitter "Twitter")
[![UK Home Office](https://pydantic.dev/docs/validation/logos/ukhomeoffice_logo.png)](https://pydantic.dev/docs/validation/latest/get-started/why/#org-ukhomeoffice "UK Home Office")
For a more comprehensive list of open-source projects using Pydantic see the [list of dependents on github](https://github.com/pydantic/pydantic/network/dependents), or you can find some awesome projects using Pydantic in [awesome-pydantic](https://github.com/Kludex/awesome-pydantic).
Was this page helpful? Thanks for your feedback!
[ Next
Why use Pydantic ](https://pydantic.dev/docs/validation/latest/get-started/why/)
© Pydantic Services Inc. 2025 to present
[ ](https://github.com/pydantic "Pydantic on GitHub") [ ](https://x.com/pydantic "Pydantic on X") [ ](https://www.linkedin.com/company/pydantic/ "Pydantic on LinkedIn") [ ](https://bsky.app/profile/pydantic.dev "Pydantic on Bluesky")
