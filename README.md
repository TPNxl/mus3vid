# Mus3Vid: Your Multimodal Foundation Model is Secretly Synesthetic 🎵➡️🎥  
*Should be called Mus2Vid. But that name's already taken.*

Mus3Vid is a Python pipeline that takes an audio file (MP3/WAV), uses **Gemini 2.5 Pro** to analyze it, generates video clips via **Google Veo 2**, and stitches everything together into a polished, synced video. Perfect for musicians, content creators, or anyone who wants custom visuals without breaking a sweat.

## Isn't this just a glorified wrapper for two foundation models?
We’re not here to reinvent the wheel. But multimodal LLMs (mLLMs) are secretly way more synesthetic and aware than they let on. Blend that with a video generation model, and suddenly you’re bridging two distinct non-text modalities without any of the usual ML overhead:
- **without** ImageBind or separate cross-modal alignment
- **without** fine-tuning - at all, just a scrambled-together prompt
- **without** fancy attention tricks or embedding-space ops designed to weld models together like conjoined twins
- and most importantly, with only a little over 300 lines of code, written on a Friday night in 4 hours with 4 hours of sleep. **Vibe coding :sparkle:**

## Features 🚀
- **Automatic Music Analysis**: Breaks down the song into sections and generates descriptive prompts using [Google's Gemini 2.5 Pro LLM](https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025).
- **AI-Powered Video Generation**: Uses [Google's Veo 2 video-generation model](https://deepmind.google/technologies/veo/veo-2/) to create unique video clips for each section.
- **Seamless Audio Sync**: Merges generated visuals and overlays the original audio.
- **Queue-Based Video Rendering**: Limits simultaneous generations for stability and efficiency.
- **Custom Prompts**: Tailor your video generation style via editable prompt templates.
- **The build quality of a Tesla**: Your take on whether that's good or bad.

⚠️ **WARNING:** This script uses real API credits and costs roughly **$23/minute of audio** to generate video. Use a **GCP free trial**. Don’t nuke your bank account.

---

## Installation ⚙️

1. **Clone the repo:**
   ```bash
   git clone https://github.com/TPNxl/mus3vid.git
   cd mus3vid
   ```

2. **Install dependencies:**
   Set up your favorite version of Python 3.13 and then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your keys and prompts:**
   - Add your Google Generative Language API key to the `keys/` folder as `google_gla.txt`. If you need one, you can go to the [Google AI Studio](https://aistudio.google.com/u/1/apikey) to get one.
   - Ensure your API key is hooked up to a billing account - **and make sure it's a $300 Google Cloud Platform (GCP) free trial, NOT your bank account**, because this script is *expensive* to run. See below.

---

## Folder Structure 📁
```
mus3vid/
├── input_files/     # Place your MP3 or WAV files here
├── output_files/    # Generated videos and cache files go here
├── keys/            # API keys (e.g., google_gla.txt)
├── prompts/         # Prompt templates for LLMs
├── mus3vid.py       # Main script
├── utils.py         # Utility functions and data models
└── README.md        # This file
```

---

## Usage 🏃‍♂️

1. **Add your audio files** (MP3 or WAV) into the `input_files/` folder.

2. **Run the script:**
   ```bash
   python mus3vid.py
   ```

3. **Watch the magic happen:**
   - The script:
     - Analyzes your audio.
     - Queues up video generations.
     - Merges everything into a final video in `output_files/`.

4. **Optional cleanup:**
   - You’ll be prompted on whether to delete existing outputs before starting.

5. **WARNING!!!**
   Running this script uses real Gemini API credits. The Veo 2 video generation API is [$0.35/second of video generated](https://ai.google.dev/gemini-api/docs/pricing)... **that means every minute of input audio costs $21 to generate video for.** And that's not even counting the LLM token credits! Be really careful with how you spend money to generate video.

#### I'll say it again: this script costs around $23 per minute of input audio to run (and generates a video of the same length).
**You are strongly advised not to use your own money for this.**

---
## Configuration options

#### Settings
- **utils.py**: Contains configuration options for the LLM used and Veo model parameters (aspect ratio, etc.)
#### Prompts
### Prompt Tuning

| Option                  | Description                                                                        | Default File                 |
|-------------------------|------------------------------------------------------------------------------------|------------------------------|
| **LLM System Prompt**    | Controls how the LLM interprets music (section breakdowns, descriptions, etc.).    | `llm_system.txt`             |
| **LLM Start Text**       | The **initial instruction** to the LLM (e.g., “Generate a video for this music…”). | `llm_start_text.txt`         |
| **Video Negative Prompt**| Defines what **not** to include in generated videos (e.g., “blurry, distorted…”).  | `vg_negative.txt`            |

---

## Known Issues 🐛
- **VEO Generation Limits**: Too many queued requests may hit rate limits. Adjust `MAX_VIDEOS_GEN` as needed. There are lots of errors when hitting rate limits. These are normal... probably.
- **No support for roll-your-own video models**: The Veo model is good, but expensive. We plan to add support for other video models in the future.
- **Prompt Sensitivity**: Prompt quality affects video outcomes-experiment with the prompts in ``./prompts/``.

---

## License 📝
MIT License.  
Use it. Break it. Build on it. Just don’t sue me if it blows up your computer... or runs up a $10k bill from Google.

---

## Credits ✨
- Purvish's [mus2vid-redux](https://github.com/pjjajal/mus2vid-redux/tree/main) repo built using [Mu-LLaMA](https://github.com/shansongliu/MU-LLaMA) as inspiration.
- **Gemini 2.5 Pro** for music analysis.
- **Google VEO** for video generation.
- **moviepy** for video stitching.
- **pydantic_ai** for model orchestration.

---

## Future Plans 💡
- Add support for **different video generation models** - Veo is expensive!
- Enable **custom audio-visual themes**.
- Implement **batch processing reports**.

---

## Contact 👋
Questions? Feature requests? Just want to vibe?  
**tnadolsk@purdue.edu**  
Feel free to fork, star, or drop a PR.
