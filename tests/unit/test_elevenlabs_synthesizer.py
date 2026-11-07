import base64
import asyncio
import json

import pytest
import httpx

import vision_caption.adapters.tts.ElevenLabsSynthesizer as adapter


class Socket:
    def __init__(self, messages):
        self.messages = iter(messages)
        self.sent = []
        self.closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.closed = True

    async def send(self, value):
        self.sent.append(json.loads(value))

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return json.dumps(next(self.messages))
        except StopIteration:
            raise StopAsyncIteration


@pytest.mark.asyncio
async def test_v4_uses_dialogue_socket_and_returns_all_mp3_chunks(monkeypatch):
    socket = Socket([{'audio':base64.b64encode(b'first').decode()}, {'is_final_audio_for_turn':True},
        {'audio':base64.b64encode(b'tail').decode()}, {'is_final':True}])
    connections = []
    def connect(uri, **kwargs):
        connections.append((uri,kwargs))
        return socket
    monkeypatch.setattr(adapter,'connect',connect)
    metrics=[]
    synth=adapter.ElevenLabsSynthesizer('secret',model_id='eleven_v4_turbo',metrics_callback=metrics.append)
    audio=await synth.synthesize('Un tavolo nero con sedie rosse.')
    assert audio.audio_bytes == b'firsttail'
    assert 'text-to-dialogue/stream-input' in connections[0][0]
    assert 'language_code=it' in connections[0][0]
    assert connections[0][1]['additional_headers']=={'xi-api-key':'secret'}
    assert socket.sent == [{'voices':['21m00Tcm4TlvDq8ikWAM']},
        {'inputs':[{'text':'Un tavolo nero con sedie rosse.','voice_id':'21m00Tcm4TlvDq8ikWAM'}]}, {'close_socket':True}]
    assert socket.closed
    assert metrics[0]['total_ms'] >= metrics[0]['first_chunk_ms']


@pytest.mark.asyncio
@pytest.mark.parametrize('messages', [[{'error':'bad input'}],[{'is_final':True}]])
async def test_v4_closes_on_provider_errors_or_empty_audio(monkeypatch,messages):
    socket=Socket(messages)
    monkeypatch.setattr(adapter,'connect',lambda *a,**k:socket)
    with pytest.raises(RuntimeError):
        await adapter.ElevenLabsSynthesizer('key',model_id='eleven_v4_turbo').synthesize('Testo')
    assert socket.closed


@pytest.mark.asyncio
async def test_v4_timeout_closes_the_socket(monkeypatch):
    class SlowSocket(Socket):
        async def __anext__(self):
            await asyncio.sleep(1)
            return '{}'
    socket=SlowSocket([])
    monkeypatch.setattr(adapter,'connect',lambda *a,**k:socket)
    with pytest.raises(TimeoutError):
        await adapter.ElevenLabsSynthesizer('key',model_id='eleven_v4_turbo',timeout_seconds=.01).synthesize('Testo')
    assert socket.closed


@pytest.mark.asyncio
async def test_existing_turbo_keeps_the_http_protocol(monkeypatch):
    seen=[]
    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(200,content=b'mp3')
    client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(adapter.httpx,'AsyncClient',lambda:client)
    audio=await adapter.ElevenLabsSynthesizer('key').synthesize('Testo italiano')
    assert audio.audio_bytes == b'mp3'
    assert seen[0]['model_id']=='eleven_turbo_v2_5'
