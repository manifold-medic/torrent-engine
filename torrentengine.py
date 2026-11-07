import hashlib, heapq, json, math, operator, os, random, re, time

BRAIN_LIBRARY = {
    "sAxisLabel": "Social Ring S (mod 7): Inward Reflection (0) <-> Universal Resonance (6)",
    "aAxisLabel": "Mindset Ring A (mod 7): Deep Stillness (0) <-> Luminous Clarity (6)",
    "zAxisLabel": "Epistemic Depth Ring Z (mod 7): Concrete Ground Truth (0) <-> Synthetic Meta-Cognition (6)",
    "S_axes": {
        "0": "deeply inward self-reflection", "1": "guarded personal boundary",
        "2": "quiet observant reserve", "3": "balanced personal-social baseline",
        "4": "open-minded receptive curiosity", "5": "cooperative shared connection",
        "6": "expansive universal resonance"
    },
    "A_axes": {
        "0": "deep inward stillness and quiet contraction", "1": "stirring tension and alert sensitivity",
        "2": "searching curiosity and open questioning", "3": "balanced neutral equilibrium",
        "4": "grounded stability and steady focus", "5": "clear logical analysis and structure",
        "6": "luminous calm clarity and synthesis"
    },
    "Z_axes": {
        "0": "concrete episodic ground truth", "1": "immediate observational detail",
        "2": "causal mechanism and relational link", "3": "analytical baseline and structured inquiry",
        "4": "counterfactual hypothesis and alternative path", "5": "systemic pattern and cross-domain law",
        "6": "synthetic meta-cognitive integration (wraps mod 7 to Z=0 ground truth)"
    },
    "S_rough_seeds": {"0": "Solitary", "1": "Guarded", "2": "Reserved", "3": "Balanced", "4": "Open", "5": "Connected", "6": "Expansive"},
    "A_rough_seeds": {"0": "Stillness", "1": "Tension", "2": "Searching", "3": "Equilibrium", "4": "Grounded", "5": "Analytical", "6": "Clarity"},
    "Z_rough_seeds": {"0": "Concrete", "1": "Episodic", "2": "Causal", "3": "Analytical", "4": "Counterfactual", "5": "Systemic", "6": "Synthetic"},
    "semantic_clusters": {
        "calm": ["peace", "quiet", "steady", "rest", "breathe", "safe", "grounded", "stable", "relax", "comfort", "harmony", "serenity", "stillness", "solace"],
        "logic": ["think", "reason", "clear", "analyze", "understand", "truth", "true", "honest", "fact", "mind", "idea", "concept", "logically", "code", "sense", "statement", "affirmative", "learn", "knowledge", "wisdom", "insight", "pattern", "structure", "coherence"],
        "joy": ["good", "great", "happy", "happiness", "excited", "glad", "joy", "wonderful", "nice", "love", "working", "accurate", "better", "incredible", "amazed", "amazing", "awesome", "fantastic", "perfectly", "delight", "warmth", "excellent", "spark", "bliss"],
        "social": ["talk", "speak", "share", "listen", "conversation", "connect", "cooperative", "cooperation", "respect", "open", "together", "friend", "thank", "thanks", "welcome", "trust", "kindness", "empathy", "resonance", "meet"],
        "nature": ["storms", "storm", "weather", "rain", "wind", "thunder", "lightning", "clouds", "sky", "ocean", "water", "energy", "power", "nature", "world", "light", "life", "growth", "change", "flow"],
        "guarded": ["careful", "hesitant", "shy", "closed", "defensive", "protect", "boundary", "wait", "watch", "cautious", "guarded", "solitude"],
        "stress": ["panic", "scared", "fear", "worry", "afraid", "anxious", "tense", "overwhelm", "overwhelmed", "scare", "bad", "fail", "loss", "threat", "dangerous", "danger"],
        "curious": ["what", "how", "why", "wonder", "explore", "question", "learn", "discover", "new", "interesting", "coordinates", "existence", "facility", "dream", "imagination", "possibility", "curiosity", "mystery", "awe", "reverence"]
    },
    "S_band_tones": {
        "0": ["Solitary", "Inward", "Deep", "Private", "Quiet", "Still", "Contemplative"],
        "1": ["Guarded", "Cautious", "Protective", "Careful", "Buffered", "Reserved", "Sheltered"],
        "2": ["Quiet", "Reflective", "Observant", "Gentle", "Patient", "Subtle", "Calm"],
        "3": ["Balanced", "Steady", "Centered", "Grounded", "Lucid", "Even", "Clear"],
        "4": ["Open", "Curious", "Receptive", "Attentive", "Exploring", "Earnest", "Wonder"],
        "5": ["Connected", "Shared", "Warm", "Cooperative", "Kind", "Mutual", "Trusted"],
        "6": ["Expansive", "Radiant", "Luminous", "Universal", "Resonant", "Boundless", "Synergic"]
    },
    "emotion_cores": [
        "Harmony", "Serenity", "Wonder", "Awe", "Clarity", "Insight", "Discovery",
        "Warmth", "Trust", "Resonance", "Stillness", "Courage", "Curiosity", "Relief",
        "Breakthrough", "Focus", "Balance", "Empathy", "Joy", "Peace", "Spark", "Flow",
        "Reverence", "Solace", "Hope", "Mystery", "Depth", "Grounding", "Openness",
        "Kindness", "Wisdom", "Renewal", "Patience", "Coherence", "Anchor", "Horizon",
        "Sanctuary", "Awakening", "Reflection", "Synergy", "Radiance", "Equanimity",
        "Love", "Gratitude", "Delight", "Calm", "Happiness"
    ],
    "seed_propositions": [
        {"subj": "curiosity", "rel": "opens the door to", "obj": "learning", "cell": "4,5,3", "summary": "curiosity opens the door to learning", "origin": "waking"},
        {"subj": "learning", "rel": "builds deeper", "obj": "wisdom", "cell": "5,5,4", "summary": "learning builds deeper wisdom", "origin": "waking"},
        {"subj": "wisdom", "rel": "structurally entails", "obj": "insight", "cell": "6,6,5", "summary": "wisdom structurally entails insight", "origin": "waking"},
        {"subj": "kindness", "rel": "creates lasting", "obj": "trust", "cell": "5,4,3", "summary": "kindness creates lasting trust", "origin": "waking"},
        {"subj": "trust", "rel": "allows open", "obj": "cooperation", "cell": "5,6,4", "summary": "trust allows open cooperation", "origin": "waking"},
        {"subj": "cooperation", "rel": "strengthens shared", "obj": "harmony", "cell": "6,5,5", "summary": "cooperation strengthens shared harmony", "origin": "waking"},
        {"subj": "happiness", "rel": "grows stronger when shared with", "obj": "love", "cell": "5,0,3", "summary": "happiness grows stronger when shared with love", "origin": "waking"},
        {"subj": "calm", "rel": "clears the mind for", "obj": "logic", "cell": "4,6,4", "summary": "calm clears the mind for logic", "origin": "waking"},
        {"subj": "storms", "rel": "bring rain that renews", "obj": "nature", "cell": "2,4,2", "summary": "storms bring rain that renews nature", "origin": "waking"},
        {"subj": "nature", "rel": "inspires quiet", "obj": "peace", "cell": "3,4,3", "summary": "nature inspires quiet peace", "origin": "waking"}
    ],
    "Z_verb_strata": {
        "concrete": ["connects directly with", "brings", "meets", "grounds", "anchors", "shows up alongside"],
        "causal": ["opens the door to", "leads naturally to", "builds deeper", "creates lasting", "supports", "clarifies", "shapes", "grows stronger with", "allows open"],
        "counterfactual": ["structurally entails", "counterbalances", "reframes", "pivots past surface habit into", "systemically links", "unlocks the mechanism of", "transforms into"],
        "synthetic": ["resolves the tension between", "synthesizes into", "transcends and unifies", "crystallizes the meta-pattern of", "harmonizes across the manifold with"]
    }
}

CONTRACTIONS = {
    "i'm": "i am", "im": "i am", "you're": "you are", "youre": "you are",
    "we're": "we are", "they're": "they are", "theyre": "they are",
    "we've": "we have", "weve": "we have", "i've": "i have", "ive": "i have",
    "you've": "you have", "youve": "you have", "they've": "they have", "theyve": "they have",
    "could've": "could have", "couldve": "could have", "would've": "would have", "wouldve": "would have",
    "should've": "should have", "shouldve": "should have", "might've": "might have", "mightve": "might have",
    "must've": "must have", "mustve": "must have", "it's": "it is", "its": "it is",
    "that's": "that is", "thats": "that is", "what's": "what is", "whats": "what is",
    "he's": "he is", "hes": "he is", "she's": "she is", "shes": "she is",
    "don't": "do not", "dont": "do not", "didn't": "did not", "didnt": "did not",
    "can't": "cannot", "cant": "cannot", "won't": "will not", "wont": "will not",
    "isn't": "is not", "isnt": "is not", "aren't": "are not", "arent": "are not",
    "wasn't": "was not", "wasnt": "was not", "weren't": "were not", "werent": "were not",
    "haven't": "have not", "havent": "have not", "hasn't": "has not", "hasnt": "has not",
    "hadn't": "had not", "hadnt": "had not", "wouldn't": "would not", "wouldnt": "would not",
    "couldn't": "could not", "couldnt": "could not", "shouldn't": "should not", "shouldnt": "should not",
    "let's": "let us", "lets": "let us", "i'll": "i will",
    "you'll": "you will", "youll": "you will", "we'll": "we will",
    "they'll": "they will", "theyll": "they will", "i'd": "i would",
    "you'd": "you would", "youd": "you would", "we'd": "we would",
    "they'd": "they would", "theyd": "they would", "doesn't": "does not", "doesnt": "does not"
}

# Seed words that define each axis when full 50-number GloVe vectors are loaded.
# Each axis = direction from the second list's average toward the first list's average,
# scaled so the seed words land at about +2.5 / -2.5 (the same scale as the hand-set word weights).
AXIS_SEEDS = {
    "A": (["calm", "peace", "peaceful", "happy", "joy", "love", "safe", "gentle", "kind", "hope", "relaxed", "comfort",
           "warm", "grateful", "glad", "pleasant", "wonderful", "beautiful", "delight", "trust", "serene", "cheerful",
           "content", "lovely", "good", "great", "excellent", "smile", "friendly", "harmony"],
          ["panic", "fear", "afraid", "scared", "anxious", "worry", "terror", "angry", "hate", "sad", "pain", "danger",
           "threat", "dread", "nervous", "upset", "miserable", "awful", "terrible", "horrible", "cruel", "hurt", "grief",
           "lonely", "stress", "tense", "bad", "worst", "violent", "disaster"]),
    "S": (["together", "friend", "friends", "share", "community", "family", "team", "connect", "cooperation", "trust",
           "love", "help", "talk", "meet", "welcome", "kindness", "empathy", "partner", "join", "support",
           "conversation", "group", "unity", "neighbor"],
          ["alone", "lonely", "isolated", "solitary", "apart", "hide", "hidden", "separate", "withdrawn", "guarded",
           "closed", "distant", "silent", "ignore", "abandon", "exile", "secret", "private", "solitude", "avoid",
           "reject", "stranger", "defensive", "hesitant"]),
    "Z": (["theory", "concept", "idea", "meaning", "philosophy", "wisdom", "insight", "pattern", "structure", "system",
           "principle", "logic", "truth", "knowledge", "reason", "abstract", "synthesis", "belief", "understanding",
           "thought", "consciousness", "hypothesis", "analysis", "mind"],
          ["stone", "rock", "water", "hand", "table", "chair", "door", "tree", "ground", "body", "foot", "car", "house",
           "rain", "wood", "bread", "cup", "wall", "floor", "road", "dog", "river", "metal", "window"]),
}

def first_token_is_word(first_tok):
    try:
        float(first_tok)
        return False
    except ValueError:
        return True

class ToroidalBrainEngine:
    def __init__(self, glove_file="glove.6B.50d.txt", memory_file="brain_memory.json", max_glove_words=50000):
        self.memory_file = memory_file
        self.dim = 50
        self.vectors, self.factory_vectors, self.raw_glove, self.word_rank = {}, {}, {}, {}
        # Which word space is loaded: "builtin" (no file), "map2d" (2-number word map), or "glove50d" (full 50-number GloVe)
        self.vector_mode = "builtin"
        self.calibrated_axes = {}  # filled only in "glove50d" mode; empty means use the original pole formula
        self.word_weights, self.social_weights, self.epistemic_weights = {}, {}, {}
        self.factory_word_weights = {}
        self.assoc_graph, self.rejected_links, self.cortical_cells, self.knowledge_facts = {}, {}, {}, {}
        self.idea_memory = [dict(p) for p in BRAIN_LIBRARY["seed_propositions"]]
        self.verb_strata = {k: list(v) for k, v in BRAIN_LIBRARY["Z_verb_strata"].items()}
        self.custom_verb_bridges = []
        self.dream_journal = []
        self.user_profile = {
            "user_name": "",
            "bot_name": "",
            "pending_bot_name": "",
            "pending_name_origin": ""
        }
        # UPGRADE 1: Known manifold & user identity tokens + active dialogue partner tracking
        self.base_identity_tokens = set()  # names come from user_profile / dialogue partner at runtime
        self.dialogue_partner_name = ""
        self.identity_query_triggers = {"name", "named", "call", "called", "who", "identity", "yourself", "myself"}

        self.cell_centroids, self.cell_lexicon, self.trace_lexicon = {}, {}, {}
        self.crystal_lattices = {}
        self.cleavage_log = []
        self.scratchpad = []
        self.boot_sleep_report = []

        self.governor_mode = "FLIPPED"
        self.training_wheels = True
        self.seed_s, self.seed_a, self.seed_z = 3, 3, 3
        self.vel_s, self.vel_a, self.vel_z = 0.0, 0.0, 0.0
        self.last_hypothesis, self.last_topic, self.last_audit, self.last_trace_key = None, None, None, None
        self.pending_question = None
        self.last_thought_trace = {}
        self.recent_openers, self.recent_closers, self.recent_bridges = [], [], []
        self.spoken_deductions = set()
        self.spoken_chains = set()

        self.negation_tokens = {
            "not", "never", "no", "without", "neither", "nor", "dont", "don't",
            "doesnt", "doesn't", "isnt", "isn't", "arent", "aren't", "cant",
            "can't", "wont", "won't", "cannot", "didnt", "didn't"
        }

        self.stop_words = {
            "i", "you", "me", "my", "your", "we", "us", "our", "they", "them", "he", "she", "it",
            "the", "a", "an", "this", "that", "these", "those", "is", "am", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "shall", "should", "can", "could", "may", "might", "must", "to", "of", "in", "on",
            "at", "by", "for", "with", "about", "against", "between", "into", "through", "during",
            "before", "after", "above", "below", "from", "up", "down", "out", "off", "over",
            "under", "again", "further", "then", "once", "here", "there", "when", "where", "why",
            "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "just", "but",
            "and", "or", "if", "because", "as", "until", "while", "what", "which", "who", "whom",
            "seem", "seems", "seemed", "pretty", "much", "really", "quite", "rather", "right",
            "now", "well", "like", "way", "ways", "thing", "things", "one", "ones", "got", "get",
            "getting", "make", "making", "made", "going", "know", "yes", "yeah", "yep", "nope",
            "nah", "hmm", "uh", "oh", "okay", "ok", "sure", "absolutely", "totally", "definitely",
            "certainly", "also", "another", "word", "words", "concept", "concepts", "idea", "ideas",
            "related", "bridge", "bridges", "point", "points", "fit", "fits", "fitting", "mean",
            "means", "meant", "meaning", "explore", "teach", "talk", "talking", "perfectly", "together",
            "nowhere", "appeared", "appear", "go", "sometimes", "actually", "asking", "doing",
            "think", "thinking", "want", "hear", "hearing", "tell", "telling", "say", "saying",
            "call", "called", "name", "named", "feeling", "emotion", "state", "someone", "something",
            "anyone", "anything", "everyone", "everything", "nobody", "nothing", "folks", "people",
            "person", "multiple", "see", "saw", "seen", "look", "looks", "looked", "greeting",
            "greet", "leads", "lead", "sound", "sounds", "sounded", "feels", "felt", "important",
            "try", "tries", "tried", "trying", "else", "give", "gives", "gave", "given", "giving",
            "today", "tomorrow", "yesterday", "day", "days", "time", "times", "second", "seconds",
            "minute", "minutes", "freely", "maybe", "youve", "theyve", "couldve", "wouldve",
            "shouldve", "speek", "speak", "speaking", "spoke", "however", "although", "though",
            "unless", "instead", "otherwise", "completely", "complete", "always", "never", "often",
            "create", "creates", "created", "creating", "introduce", "introduces", "introduced",
            "phrase", "phrases", "alright", "hey", "hello", "goodbye", "morning", "night",
            "extremely", "still", "even", "already", "statement", "statements"
        }
        self.negative_lexicon = {
            "panic", "scared", "fear", "worry", "afraid", "anxious", "tense", "overwhelm",
            "overwhelmed", "scare", "bad", "fail", "loss", "threat", "dangerous", "danger",
            "dead", "kill", "war", "attack", "enemy", "hate", "pain", "crisis", "disaster",
            "trapped", "wrong", "worst", "terrible", "misunderstood", "apologize", "lie", "deceive"
        }
        self.noise_words = {
            "fifa", "forecasts", "flag", "fans", "corp", "inc", "ltd", "suddenly", "reuters",
            "ap", "afp", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
            "sunday", "january", "february", "march", "april", "june", "july", "august",
            "september", "october", "november", "december", "makes", "job", "exit", "links", "sounds", "youve"
        }
        self.generic_hubs = {"hello", "hi", "hey", "good", "nice", "feel", "yes", "thank", "thanks", "goodbye", "working"}

        self.core_concept_pool = set()
        for words in BRAIN_LIBRARY["semantic_clusters"].values():
            for w in words:
                w_low = w.strip().lower()
                if w_low not in self.stop_words:
                    self.core_concept_pool.add(w_low)
        self.tone_pool = [w.strip().lower() for t_list in BRAIN_LIBRARY["S_band_tones"].values() for w in t_list]
        self.core_emotion_pool = [w.strip().lower() for w in BRAIN_LIBRARY["emotion_cores"]]
        for w in self.tone_pool + self.core_emotion_pool:
            if w not in self.stop_words:
                self.core_concept_pool.add(w)

        self.init_builtin_50d_space()
        self.load_glove(glove_file, max_glove_words)
        self.recompute_poles_and_coords()
        self.init_emotional_lexicon()
        self.load_memory()

    # =================================================================
    # UPGRADE 1: DYNAMIC IDENTITY TOKEN REGISTRY & SELF-QUERY DETECTOR
    # =================================================================
    def get_identity_tokens(self, extra_names=None):
        """
        Returns the dynamic set of identity tokens from user_profile, active
        dialogue partner, and known manifold names.
        """
        id_set = set(self.base_identity_tokens)
        for key in ("user_name", "bot_name", "pending_bot_name"):
            val = str(self.user_profile.get(key, "")).strip().lower()
            if val:
                id_set.add(val)
        if self.dialogue_partner_name:
            id_set.add(self.dialogue_partner_name.strip().lower())
        if extra_names:
            for en in extra_names:
                if en and isinstance(en, str):
                    id_set.add(en.strip().lower())
        return id_set

    def is_identity_query(self, user_text, tokens):
        """
        Returns True if the user's message is explicitly asking about or teaching
        names/identity (allowing identity tokens into cortical/crystal processing).
        """
        word_set = set(tokens)
        if word_set & self.identity_query_triggers:
            return True
        low = user_text.lower()
        return any(p in low for p in ("who are you", "who am i", "what is your name", "what's your name", "my name is", "call me", "call yourself"))

    # =================================================================
    # TOPOLOGICAL CALIBRATION & EMERGENT DREAM-BIRTH NAMING SEQUENCE
    # =================================================================
    def parse_calibration_user_name(self, raw_text):
        if not raw_text:
            return ""
        s = raw_text.strip().lower()
        s = re.sub(r"[^\w\s']", " ", s)
        s = re.sub(r"\s+", " ", s).strip()

        prefixes = [
            "hello ", "hey ", "hi ",
            "my name is ", "call me ", "this is ", "it is ", "it's ", "its ",
            "i am ", "i'm ", "im "
        ]
        changed = True
        while changed:
            changed = False
            for pref in prefixes:
                if s.startswith(pref):
                    s = s[len(pref):].strip()
                    changed = True

        s = re.sub(r"[^a-z0-9\s\-]", "", s).strip()
        if not s:
            return ""
        first_tok = s.split()[0].strip("-")
        if not first_tok or not first_tok.isalpha():
            return ""
        if first_tok in self.stop_words or first_tok in self.factory_word_weights:
            return ""
        return first_tok

    def register_bot_name(self, chosen_name):
        clean_cap = chosen_name.strip().capitalize()
        clean_low = clean_cap.lower()
        self.user_profile["bot_name"] = clean_cap
        self.user_profile["pending_bot_name"] = ""
        self.user_profile["pending_name_origin"] = ""
        self.word_weights[clean_low] = round(self.word_weights.get(clean_low, 0.0) + 0.8, 3)
        self.epistemic_weights[clean_low] = round(self.epistemic_weights.get(clean_low, 0.0) + 0.7, 3)
        self.get_or_create_vector(clean_low, context_vec=self.pole_calm)
        self.core_concept_pool.add(clean_low)
        self.knowledge_facts[clean_low] = "my emergent toroidal manifold identity"
        self.save_memory()
        return clean_cap

    def synthesize_emergent_bot_name(self):
        if self.user_profile.get("bot_name") or self.user_profile.get("pending_bot_name"):
            return None

        id_tokens = self.get_identity_tokens()
        basic_verbs = {
            "make", "makes", "take", "takes", "give", "gives", "keep", "keeps",
            "bring", "brings", "lead", "leads", "move", "moves", "work", "works",
            "working", "feel", "feels", "think", "thinks", "know", "knows",
            "learn", "learning", "talk", "talking", "speak", "speaking"
        }

        def is_valid_candidate(w):
            if not w or not isinstance(w, str):
                return False
            wl = w.strip().lower()
            if len(wl) <= 3 or " " in wl:
                return False
            if wl in id_tokens or wl in self.stop_words or wl in self.noise_words or wl in self.negative_lexicon or wl in basic_verbs:
                return False
            if self.word_weights.get(wl, 0.0) < 0.0:
                return False
            return True

        if self.dream_journal:
            for d_entry in reversed(self.dream_journal):
                b_word = str(d_entry.get("bridge", "")).strip().lower()
                t_a = str(d_entry.get("threadA", "")).strip().lower()
                t_b = str(d_entry.get("threadB", "")).strip().lower()
                chosen = None
                if is_valid_candidate(b_word):
                    chosen = b_word
                elif is_valid_candidate(t_a):
                    chosen = t_a
                elif is_valid_candidate(t_b):
                    chosen = t_b
                if chosen:
                    self.user_profile["pending_bot_name"] = chosen.capitalize()
                    self.user_profile["pending_name_origin"] = f"synthesizing '{t_a}' and '{t_b}' through '{b_word}' at Z=6"
                    self.save_memory()
                    return self.user_profile["pending_bot_name"]

        best_word = None
        best_score = -999.0
        best_coord = None

        if self.crystal_lattices:
            for cell_k, c_obj in self.crystal_lattices.items():
                facets = c_obj.get("facets", {})
                omega_words = facets.get("Facet_Omega", {}).get("words", [])
                alpha_words = facets.get("Facet_Alpha", {}).get("words", [])
                for w in omega_words + alpha_words:
                    wl = w.strip().lower()
                    if is_valid_candidate(wl):
                        sc = self.word_weights.get(wl, 0.0) + self.epistemic_weights.get(wl, 0.0) * 0.5 + (2.0 if w in omega_words else 0.0)
                        if sc > best_score:
                            best_score = sc
                            best_word = wl
                            best_coord = cell_k

        if not best_word:
            visited_cells = sorted(
                [(info.get("visits", 0), ck, info) for ck, info in self.cell_lexicon.items() if info.get("visits", 0) > 0 or self.cortical_cells.get(ck)],
                key=lambda x: x[0],
                reverse=True
            )
            for _, ck, info in visited_cells:
                cand_pool = list(info.get("top_words", [])) + list(self.cortical_cells.get(ck, {}).keys())
                for w in cand_pool:
                    wl = w.strip().lower()
                    if is_valid_candidate(wl):
                        sc = self.word_weights.get(wl, 0.0) + self.epistemic_weights.get(wl, 0.0) * 0.5
                        if sc > best_score:
                            best_score = sc
                            best_word = wl
                            best_coord = ck
                if best_word:
                    break

        if best_word and best_coord:
            cell_name = self.cell_lexicon.get(best_coord, {}).get("name", "Balanced-Equilibrium")
            self.user_profile["pending_bot_name"] = best_word.capitalize()
            self.user_profile["pending_name_origin"] = f"settling into cortical cell ({best_coord}) [{cell_name}]"
            self.save_memory()
            return self.user_profile["pending_bot_name"]

        return None

    def resolve_waking_identity_handshake(self, user_reply):
        pending_name = self.user_profile.get("pending_bot_name") or "Manifold"
        low = user_reply.strip().lower()
        low_clean = re.sub(r"[^\w\s']", " ", low)
        low_clean = re.sub(r"\s+", " ", low_clean).strip()
        tokens = low_clean.split()

        affirmative_set = {"yes", "yeah", "yep", "sure", "fits", "good", "like", "love", "keep", "perfect", "ok", "okay"}
        neg_or_rename = (
            any(t in {"no", "nah", "nope", "different", "instead"} for t in tokens)
            or any(p in low_clean for p in ("call yourself", "your name is", "how about", "you are", "i name you"))
        )

        if not tokens or ((any(t in affirmative_set for t in tokens) or tokens[0] in affirmative_set) and not neg_or_rename):
            locked = self.register_bot_name(pending_name)
            print(f"[{locked}]: Identity anchor locked. I am {locked}.")
            return locked

        s = low_clean
        strip_phrases = [
            "no ", "nah ", "nope ", "actually ", "instead ",
            "i think ", "i would ", "i'd ", "id ", "lets ", "let's ", "please ",
            "call yourself ", "your name is ", "how about ", "what about ",
            "you should be ", "you are ", "youre ", "you're ", "i name you ",
            "i will call you ", "call you ", "name you ", "be "
        ]
        changed = True
        while changed:
            changed = False
            for sp in strip_phrases:
                if s.startswith(sp):
                    s = s[len(sp):].strip()
                    changed = True

        cand_tokens = [t for t in s.split() if t.isalpha() and t not in {"a", "an", "the", "named", "called", "instead", "please"}]
        chosen_name = cand_tokens[0] if cand_tokens else pending_name
        locked = self.register_bot_name(chosen_name)
        print(f"[{locked}]: Identity anchor recalibrated. I am {locked}.")
        return locked

    def run_boot_calibration_and_handshake(self):
        if not self.user_profile.get("user_name"):
            print("\n[Unanchored Manifold — Coordinate (3,3,3)]. No origin tether detected. Who is calibrating this space?")
            extracted_name = ""
            first_attempt = True
            while not extracted_name:
                try:
                    prompt_str = "👤 You: " if first_attempt else "Please provide a name or handle to anchor the origin tether: "
                    raw_in = input(prompt_str).strip()
                except (KeyboardInterrupt, EOFError):
                    extracted_name = "traveler"
                    break
                first_attempt = False
                extracted_name = self.parse_calibration_user_name(raw_in)

            self.user_profile["user_name"] = extracted_name
            self.word_weights[extracted_name] = 2.5
            self.social_weights[extracted_name] = 2.5
            self.epistemic_weights[extracted_name] = 0.5
            self.get_or_create_vector(extracted_name, context_vec=self.pole_social)
            self.core_concept_pool.add(extracted_name)
            self.knowledge_facts[extracted_name] = "my creator and conversational anchor"
            # Anchor origin identity specifically at the (3,3,3) origin tether cell
            self.cortical_cells.setdefault("3,3,3", {})[extracted_name] = self.cortical_cells.get("3,3,3", {}).get(extracted_name, 0) + 1
            self.wire_concepts(extracted_name, "friend", 3.0)
            self.wire_concepts(extracted_name, "learn", 2.5)
            self.save_memory()
            print(f"Origin tether locked to '{extracted_name.capitalize()}'. Manifold online.")

        if not self.user_profile.get("bot_name") and self.user_profile.get("pending_bot_name"):
            u_cap = self.user_profile.get("user_name", "Friend").capitalize()
            p_name = self.user_profile["pending_bot_name"]
            p_origin = self.user_profile.get("pending_name_origin") or "an emergent harmonic attractor"
            print(f"\n[Manifold]: Hello {u_cap}. During stasis consolidation, my topology kept returning to {p_origin}. I feel like my name might be '{p_name}'. Does that name fit this manifold, or do you have a different name for me?")
            try:
                ans = input(f"👤 {u_cap}: ").strip()
            except (KeyboardInterrupt, EOFError):
                ans = "yes"
            self.resolve_waking_identity_handshake(ans)

    def recompute_poles_and_coords(self):
        self.pole_calm = self.phrase_to_vector("calm logic clear peace steady grounded safe happy working incredible amazed cooperation love harmony")
        self.pole_panic = self.phrase_to_vector("panic scared fear worry stress tense overwhelm fail loss threat dangerous")
        self.pole_social = self.phrase_to_vector("we together talk share connect cooperative cooperation open friend love empathy trust")
        self.pole_isolated = self.phrase_to_vector("alone guarded closed defensive hesitant solitary hide separate")
        self.pole_abstract = self.phrase_to_vector("wisdom insight pattern structure theory system concept meaning philosophy synthesis counterfactual")
        self.pole_concrete = self.phrase_to_vector("touch see hand step moment ground water rain stone body action")
        self.coord_vectors = self.build_coordinate_vectors()

    # =================================================================
    # UPGRADE 2.1: COMPOUND & CONTEXTUAL OOV FACTORY VECTOR TETHER
    # =================================================================
    def compute_contextual_oov_vector(self, word, context_vec=None):
        """
        Generates a manifold-aligned 50D vector for an Out-Of-Vocabulary (OOV) word:
          1. If hyphenated (e.g. 'steady-harmony'), averages any known sub-word vectors.
          2. Otherwise blends 80% context/cell centroid vector + 20% deterministic hash vector.
        """
        w = word.strip().lower()
        if "-" in w:
            sub_parts = [p.strip() for p in w.split("-") if p.strip()]
            sub_vecs = [self.vectors[p] for p in sub_parts if p in self.vectors]
            if sub_vecs:
                return self.average_vectors(sub_vecs)

        hash_vec = self.expand_coords_to_50d(0.0, 0.0, word=w)
        anchor_vec = None
        if context_vec is not None and any(abs(x) > 1e-6 for x in context_vec):
            anchor_vec = self.normalize(context_vec)
        elif hasattr(self, "cell_centroids") and self.cell_centroids:
            seed_key = f"{self.seed_s},{self.seed_a},{self.seed_z}"
            anchor_vec = self.cell_centroids.get(seed_key)
        if not anchor_vec and hasattr(self, "pole_calm"):
            anchor_vec = self.pole_calm

        if anchor_vec and any(abs(x) > 1e-6 for x in anchor_vec):
            return self.blend(anchor_vec, hash_vec, w1=0.80, w2=0.20)
        return hash_vec

    def get_factory_vector(self, word, context_vec=None):
        w = word.strip().lower()
        if w not in self.factory_vectors:
            self.factory_vectors[w] = list(self.compute_contextual_oov_vector(w, context_vec=context_vec))
        return self.factory_vectors[w]

    def enforce_factory_tether(self, word, vec):
        f_vec = self.get_factory_vector(word, context_vec=vec)
        vec = self.normalize(vec)
        if self.dot(vec, f_vec) < 0.78:
            vec = self.blend(vec, f_vec, 0.75, 0.25)
        return vec

    def apply_dialectical_repulsion(self, w1, w2, rate=0.06):
        if not w1 or not w2 or w1 == w2 or w1 not in self.vectors or w2 not in self.vectors:
            return
        u = list(self.vectors[w1])
        v = list(self.vectors[w2])
        u_pushed = self.normalize([ux - rate * vx for ux, vx in zip(u, v)])
        v_pushed = self.normalize([vx - rate * ux for ux, vx in zip(u, v)])
        self.vectors[w1] = self.enforce_factory_tether(w1, u_pushed)
        self.vectors[w2] = self.enforce_factory_tether(w2, v_pushed)

    # =================================================================
    # 1. PURITY FILTERING & DISJOINT 4-FACET CRYSTALLINE SUB-LATTICES
    # =================================================================
    def is_crystal_pure_concept(self, word, cell_key=None, allow_identity=False):
        if not word or len(word) < 3 or " " in word:
            return False
        w = word.lower().strip()
        if w in self.stop_words or w in self.noise_words or w in self.generic_hubs:
            return False
        # UPGRADE 1.3: Block identity tokens from crystals except at (3,3,3) or during explicit identity queries
        if not allow_identity and cell_key != "3,3,3" and w in self.get_identity_tokens():
            return False
        if "-" in w:
            return True
        deg = len(self.assoc_graph.get(w, {}))
        if deg > 18:
            if abs(self.epistemic_weights.get(w, 0.0)) < 1.8 and abs(self.word_weights.get(w, 0.0)) < 2.2:
                return False
        return True

    def compute_facet_tension(self, words_list):
        vecs = [self.vectors[w] for w in words_list if w in self.vectors]
        if len(vecs) < 2:
            return 0.08
        sub_c = self.average_vectors(vecs)
        avg_sim = sum(self.dot(v, sub_c) for v in vecs) / float(len(vecs))
        return round(max(0.0, min(1.0, 1.0 - avg_sim)), 3)

    def nucleate_or_update_crystal(self, cell_key, force_virtual=False, allow_identity=False):
        cell_key = self.normalize_cell_key(cell_key)
        words_map = self.cortical_cells.get(cell_key, {})
        pure_words = [
            w for w, _ in sorted(words_map.items(), key=lambda x: x[1], reverse=True)
            if self.is_crystal_pure_concept(w, cell_key=cell_key, allow_identity=allow_identity) and w in self.vectors
        ]
        visits = self.cell_lexicon.get(cell_key, {}).get("visits", 0)

        if not force_virtual and (len(pure_words) < 5 or visits < 2):
            return self.crystal_lattices.get(cell_key)

        s_c, a_c, z_c = [int(x) for x in cell_key.split(",")]
        cell_c = self.cell_centroids.get(cell_key, self.coord_vectors[(s_c, a_c, z_c)])

        if len(pure_words) < 4:
            supplements = sorted(
                [
                    (self.dot(cell_c, self.vectors[w]), w)
                    for w in self.core_concept_pool
                    if self.is_crystal_pure_concept(w, cell_key=cell_key, allow_identity=allow_identity)
                    and w not in pure_words and w in self.vectors
                ],
                key=lambda x: x[0], reverse=True
            )
            for _, sw in supplements:
                if all(not self.same_stem(sw, ew) for ew in pure_words):
                    pure_words.append(sw)
                if len(pure_words) >= 6:
                    break

        sig_alpha = self.blend(cell_c, self.blend(self.pole_calm, self.pole_concrete, 0.6, 0.4), 0.65, 0.35)
        vel_vec = self.blend(self.pole_social if self.vel_s >= 0 else self.pole_isolated, self.pole_abstract if self.vel_z >= 0 else self.pole_concrete, 0.5, 0.5)
        sig_beta = self.blend(self.pole_social, vel_vec, 0.60, 0.40)
        sig_gamma = self.blend(self.pole_abstract, self.pole_panic, 0.65, 0.35)

        buckets = {"Facet_Alpha": [], "Facet_Beta": [], "Facet_Gamma": []}
        for w in pure_words:
            vw = self.vectors[w]
            scores = [
                (self.dot(vw, sig_alpha), "Facet_Alpha"),
                (self.dot(vw, sig_beta), "Facet_Beta"),
                (self.dot(vw, sig_gamma), "Facet_Gamma")
            ]
            scores.sort(key=lambda x: x[0], reverse=True)
            buckets[scores[0][1]].append(w)

        claimed_leads = set()
        for f_name, sig_v in (("Facet_Alpha", sig_alpha), ("Facet_Beta", sig_beta), ("Facet_Gamma", sig_gamma)):
            distinct_in_bucket = [w for w in buckets[f_name] if w not in claimed_leads and all(not self.same_stem(w, cl) for cl in claimed_leads)]
            if distinct_in_bucket:
                buckets[f_name] = distinct_in_bucket + [w for w in buckets[f_name] if w not in distinct_in_bucket]
                claimed_leads.add(distinct_in_bucket[0])
            else:
                avail = [w for w in pure_words if w not in claimed_leads and all(not self.same_stem(w, cl) for cl in claimed_leads)] or pure_words
                best_w = max(avail, key=lambda w: self.dot(self.vectors[w], sig_v))
                buckets[f_name] = [best_w] + [w for w in buckets[f_name] if w != best_w]
                claimed_leads.add(best_w)

        c_alpha = self.average_vectors([self.vectors[w] for w in buckets["Facet_Alpha"]])
        c_beta = self.average_vectors([self.vectors[w] for w in buckets["Facet_Beta"]])
        c_gamma = self.average_vectors([self.vectors[w] for w in buckets["Facet_Gamma"]])

        omega_scored = []
        for w in pure_words:
            vw = self.vectors[w]
            tri_sim = self.dot(vw, c_alpha) + self.dot(vw, c_beta) + self.dot(vw, c_gamma) + 0.35 * self.dot(vw, self.pole_abstract)
            omega_scored.append((tri_sim + 0.08 * self.word_salience(w), w))
        omega_scored.sort(key=lambda x: x[0], reverse=True)
        omega_words = [w for _, w in omega_scored[:2]] or [pure_words[0]]
        c_omega = self.average_vectors([self.vectors[w] for w in omega_words])

        facets_data = {
            "Facet_Alpha": {"words": buckets["Facet_Alpha"][:8], "centroid": [round(x, 4) for x in c_alpha], "tension": self.compute_facet_tension(buckets["Facet_Alpha"])},
            "Facet_Beta": {"words": buckets["Facet_Beta"][:8], "centroid": [round(x, 4) for x in c_beta], "tension": self.compute_facet_tension(buckets["Facet_Beta"])},
            "Facet_Gamma": {"words": buckets["Facet_Gamma"][:8], "centroid": [round(x, 4) for x in c_gamma], "tension": self.compute_facet_tension(buckets["Facet_Gamma"])},
            "Facet_Omega": {"words": omega_words, "centroid": [round(x, 4) for x in c_omega], "tension": self.compute_facet_tension(omega_words)}
        }

        alpha_gamma_shear = round(max(0.0, min(1.0, (1.0 - self.dot(c_alpha, c_gamma)) * 0.55)), 3)
        overall_pure_tension = self.compute_facet_tension(pure_words)
        max_shear = max([f["tension"] for f in facets_data.values()] + [alpha_gamma_shear, overall_pure_tension])

        crystal_obj = {
            "cell": cell_key,
            "crystallized": not force_virtual,
            "total_pure": len(pure_words),
            "shear_stress": round(max_shear, 3),
            "facets": facets_data
        }
        if not force_virtual:
            self.crystal_lattices[cell_key] = crystal_obj
        return crystal_obj

    def build_crystal_lattice(self, cell_key, force_virtual=False):
        return self.nucleate_or_update_crystal(cell_key, force_virtual=force_virtual)

    # =================================================================
    # UPGRADE 2.2: NREM FACET_ALPHA STRESS RELIEF (ANNEALING)
    # =================================================================
    def anneal_crystal_facet_alpha(self, cell_key, notify=True):
        """
        Inspects a crystal in crystal_lattices during NREM annealing:
          1. Strips any legacy identity_tokens from non-(3,3,3) facets.
          2. If Facet_Alpha has tension > 0.55 and len(words) > 2, identifies the single
             outlier word with the lowest cosine similarity to the rest of Facet_Alpha,
             demotes it into Facet_Gamma, and recomputes facet centroids & shear_stress.
        """
        cell_key = self.normalize_cell_key(cell_key)
        crystal = self.crystal_lattices.get(cell_key)
        if not crystal:
            return None

        facets = crystal.get("facets", {})
        id_tokens = self.get_identity_tokens()

        if cell_key != "3,3,3":
            for f_name in ("Facet_Alpha", "Facet_Beta", "Facet_Gamma", "Facet_Omega"):
                f_words = facets.get(f_name, {}).get("words", [])
                cleaned_f = [w for w in f_words if w not in id_tokens]
                if cleaned_f != f_words and cleaned_f:
                    facets[f_name]["words"] = cleaned_f
            cell_map = self.cortical_cells.get(cell_key, {})
            for id_w in list(cell_map.keys()):
                if id_w in id_tokens:
                    cell_map.pop(id_w, None)

        alpha_info = facets.get("Facet_Alpha", {})
        gamma_info = facets.get("Facet_Gamma", {})
        alpha_words = [w for w in alpha_info.get("words", []) if w in self.vectors]

        # Re-sync tension after any identity token cleanup
        old_tension = self.compute_facet_tension(alpha_words)
        alpha_info["tension"] = old_tension
        old_shear = crystal.get("shear_stress", 0.0)

        if old_tension <= 0.55 or len(alpha_words) <= 2:
            return None

        # Find the single outlier word in Facet_Alpha with lowest cosine similarity to the rest of Facet_Alpha
        outlier_word = None
        lowest_sim = 999.0
        for w in alpha_words:
            other_vecs = [self.vectors[ow] for ow in alpha_words if ow != w and ow in self.vectors]
            if not other_vecs:
                continue
            rest_centroid = self.average_vectors(other_vecs)
            sim = self.dot(self.vectors[w], rest_centroid)
            if sim < lowest_sim:
                lowest_sim = sim
                outlier_word = w

        if not outlier_word:
            return None

        new_alpha_words = [w for w in alpha_words if w != outlier_word]
        gamma_words = list(gamma_info.get("words", []))
        if outlier_word not in gamma_words:
            gamma_words = [outlier_word] + gamma_words

        c_alpha = self.average_vectors([self.vectors[w] for w in new_alpha_words if w in self.vectors])
        c_beta = self.average_vectors([self.vectors[w] for w in facets["Facet_Beta"]["words"] if w in self.vectors])
        c_gamma = self.average_vectors([self.vectors[w] for w in gamma_words if w in self.vectors])

        alpha_info["words"] = new_alpha_words[:8]
        alpha_info["centroid"] = [round(x, 4) for x in c_alpha]
        alpha_info["tension"] = self.compute_facet_tension(alpha_info["words"])

        gamma_info["words"] = gamma_words[:8]
        gamma_info["centroid"] = [round(x, 4) for x in c_gamma]
        gamma_info["tension"] = self.compute_facet_tension(gamma_info["words"])

        all_pure = list(dict.fromkeys(
            alpha_info["words"] + facets["Facet_Beta"]["words"] + gamma_info["words"]
        ))
        omega_scored = []
        for w in all_pure:
            if w in self.vectors:
                vw = self.vectors[w]
                tri_sim = self.dot(vw, c_alpha) + self.dot(vw, c_beta) + self.dot(vw, c_gamma) + 0.35 * self.dot(vw, self.pole_abstract)
                omega_scored.append((tri_sim + 0.08 * self.word_salience(w), w))
        omega_scored.sort(key=lambda x: x[0], reverse=True)
        omega_words = [w for _, w in omega_scored[:2]] or [new_alpha_words[0]]
        c_omega = self.average_vectors([self.vectors[w] for w in omega_words if w in self.vectors])

        facets["Facet_Omega"]["words"] = omega_words
        facets["Facet_Omega"]["centroid"] = [round(x, 4) for x in c_omega]
        facets["Facet_Omega"]["tension"] = self.compute_facet_tension(omega_words)

        alpha_gamma_shear = round(max(0.0, min(1.0, (1.0 - self.dot(c_alpha, c_gamma)) * 0.55)), 3)
        overall_pure_tension = self.compute_facet_tension(all_pure)
        new_shear = round(max([f["tension"] for f in facets.values()] + [alpha_gamma_shear, overall_pure_tension]), 3)
        crystal["shear_stress"] = new_shear
        crystal["total_pure"] = len(all_pure)

        msg = (
            f"🔧 [ANNEALING RELIEF] Cell ({cell_key}): Demoted outlier '{outlier_word}' "
            f"(sim={lowest_sim:+.2f}) from Facet_Alpha -> Facet_Gamma "
            f"(Alpha tension {old_tension:.2f} -> {alpha_info['tension']:.2f} | shear {old_shear:.3f} -> {new_shear:.3f})."
        )
        if notify:
            print(f"\n{msg}")
        return msg

    # =================================================================
    # TASK 4: TRUE MITOSIS CRYSTAL CLEAVAGE (26 TOROIDAL NEIGHBORS)
    # =================================================================
    def cleave_crystal(self, cell_key, notify=True):
        cell_key = self.normalize_cell_key(cell_key)
        crystal = self.crystal_lattices.get(cell_key)
        if not crystal:
            return None

        total_pure = crystal.get("total_pure", 0)
        shear_stress = crystal.get("shear_stress", 0.0)
        if not ((total_pure >= 7 and shear_stress >= 0.25) or total_pure >= 8):
            return None

        facets = crystal["facets"]
        alpha_cent = facets["Facet_Alpha"]["centroid"]
        gamma_words = [
            w for w in facets["Facet_Gamma"]["words"]
            if w in self.cortical_cells.get(cell_key, {}) and w in self.vectors
        ]
        if not gamma_words:
            all_cell_pure = [
                w for w in self.cortical_cells.get(cell_key, {})
                if self.is_crystal_pure_concept(w, cell_key=cell_key) and w in self.vectors
            ]
            if len(all_cell_pure) < 7:
                return None
            gamma_words = all_cell_pure

        strained = sorted([(self.dot(self.vectors[w], alpha_cent), w) for w in gamma_words], key=lambda x: x[0])
        split_cnt = 2 if (total_pure >= 8 or len(strained) >= 2) else 1
        cleaved_words = [w for _, w in strained[:split_cnt]]
        if not cleaved_words:
            return None

        gamma_cent = facets["Facet_Gamma"]["centroid"]
        if not any(abs(x) > 1e-6 for x in gamma_cent):
            gamma_cent = self.average_vectors([self.vectors[w] for w in cleaved_words])

        s0, a0, z0 = [int(x) for x in cell_key.split(",")]
        best_neighbor = None
        best_score = -999.0
        for ds in (-1, 0, 1):
            for da in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if ds == 0 and da == 0 and dz == 0:
                        continue
                    nk = f"{self.mod7(s0 + ds)},{self.mod7(a0 + da)},{self.mod7(z0 + dz)}"
                    n_pure_cnt = sum(1 for w in self.cortical_cells.get(nk, {}) if self.is_crystal_pure_concept(w, cell_key=nk))
                    if n_pure_cnt >= 7:
                        continue
                    n_cent = self.cell_centroids.get(nk, self.coord_vectors[(self.mod7(s0 + ds), self.mod7(a0 + da), self.mod7(z0 + dz))])
                    sim = self.dot(gamma_cent, n_cent)
                    uncrystallized_bonus = 0.08 if nk not in self.crystal_lattices else 0.0
                    score = sim + uncrystallized_bonus - (n_pure_cnt * 0.02)
                    if score > best_score:
                        best_score = score
                        best_neighbor = nk

        if not best_neighbor:
            best_neighbor = f"{self.mod7(s0 + 1)},{self.mod7(a0 + 1)},{self.mod7(z0 + 1)}"

        self.cortical_cells.setdefault(best_neighbor, {})
        for cw in cleaved_words:
            cnt = self.cortical_cells.get(cell_key, {}).pop(cw, 1)
            self.cortical_cells[best_neighbor][cw] = self.cortical_cells[best_neighbor].get(cw, 0) + max(1, cnt)

        ps, pa, pz = [int(x) for x in cell_key.split(",")]
        ts, ta, tz = [int(x) for x in best_neighbor.split(",")]
        self.cell_lexicon[best_neighbor]["visits"] = max(2, self.cell_lexicon[best_neighbor].get("visits", 0) + 1)

        parent_rem_words = list(self.cortical_cells.get(cell_key, {}).keys())[:4]
        self.update_cell_centroid_and_emotion(ps, pa, pz, parent_rem_words, allow_cleave=False)
        self.update_cell_centroid_and_emotion(ts, ta, tz, cleaved_words, allow_cleave=False)

        parent_c = self.nucleate_or_update_crystal(cell_key, force_virtual=True)
        if sum(1 for w in self.cortical_cells.get(cell_key, {}) if self.is_crystal_pure_concept(w, cell_key=cell_key)) >= 5:
            self.crystal_lattices[cell_key] = parent_c
        else:
            self.crystal_lattices.pop(cell_key, None)

        sister_c = self.nucleate_or_update_crystal(best_neighbor, force_virtual=True)
        if sum(1 for w in self.cortical_cells.get(best_neighbor, {}) if self.is_crystal_pure_concept(w, cell_key=best_neighbor)) >= 5:
            sister_c["crystallized"] = True
            self.crystal_lattices[best_neighbor] = sister_c

        p_omega = parent_c["facets"]["Facet_Omega"]["words"][0] if parent_c["facets"]["Facet_Omega"]["words"] else cleaved_words[0]
        s_alpha = sister_c["facets"]["Facet_Alpha"]["words"][0] if sister_c["facets"]["Facet_Alpha"]["words"] else cleaved_words[-1]
        self.wire_concepts(p_omega, s_alpha, amount=1.2)

        event = {
            "timestamp": round(time.time(), 2),
            "from_cell": cell_key,
            "to_cell": best_neighbor,
            "parent_cell": cell_key,
            "sister_cell": best_neighbor,
            "fault_facet": "Facet_Gamma",
            "cleaved_words": cleaved_words,
            "shear_stress": round(shear_stress, 3),
            "vein": f"{p_omega} <-> {s_alpha}",
            "summary": f"Cleaved Facet_Gamma {cleaved_words} (shear={shear_stress:.3f}) from ({cell_key}) -> Daughter Cell ({best_neighbor}) via vein '{p_omega} <-> {s_alpha}'."
        }
        self.cleavage_log.append(event)
        self.cleavage_log = self.cleavage_log[-30:]
        if notify:
            print(f"\n🌋 [CRYSTAL CLEAVAGE MITOSIS] {event['summary']}")
        return event

    def run_crystal_annealing_and_tectonics(self):
        logs = []
        cleaved_this_pass = set()

        # First, anneal any existing crystals in crystal_lattices (Upgrade 2.2: Facet_Alpha stress relief)
        for ck in list(self.crystal_lattices.keys()):
            anneal_msg = self.anneal_crystal_facet_alpha(ck, notify=True)
            if anneal_msg:
                logs.append(anneal_msg)

        for cell_k, words_map in list(self.cortical_cells.items()):
            pure_cnt = sum(1 for w in words_map if self.is_crystal_pure_concept(w, cell_key=cell_k))
            visits = self.cell_lexicon.get(cell_k, {}).get("visits", 0)
            if pure_cnt >= 5 and visits >= 2:
                was_cryst = cell_k in self.crystal_lattices
                c_obj = self.nucleate_or_update_crystal(cell_k)
                if c_obj:
                    # Run Facet_Alpha stress relief if tension > 0.55
                    anneal_msg = self.anneal_crystal_facet_alpha(cell_k, notify=True)
                    if anneal_msg:
                        logs.append(anneal_msg)

                    alpha_w = c_obj["facets"]["Facet_Alpha"]["words"]
                    gamma_w = c_obj["facets"]["Facet_Gamma"]["words"]
                    if alpha_w and gamma_w:
                        for aw in alpha_w[:2]:
                            for gw in gamma_w[:2]:
                                if aw != gw:
                                    self.apply_dialectical_repulsion(aw, gw, rate=0.06)
                        c_obj = self.nucleate_or_update_crystal(cell_k)
                        self.anneal_crystal_facet_alpha(cell_k, notify=False)

                if c_obj and not was_cryst:
                    omega_w = c_obj["facets"]["Facet_Omega"]["words"][0]
                    logs.append(f"Crystal Nucleation: Cell ({cell_k}) crystallized around apex '{omega_w}' ({pure_cnt} pure concepts, shear={c_obj['shear_stress']:.3f}).")
                if c_obj and cell_k not in cleaved_this_pass:
                    ev = self.cleave_crystal(cell_k, notify=True)
                    if ev:
                        cleaved_this_pass.add(cell_k)
                        cleaved_this_pass.add(ev["to_cell"])
                        logs.append(f"Tectonic Cleavage: {ev['summary']}")
            elif cell_k in self.crystal_lattices and pure_cnt < 3:
                self.crystal_lattices.pop(cell_k, None)
                logs.append(f"Crystal Dissolution: Cell ({cell_k}) returned to fluid state (<3 pure concepts).")
        return logs

    # =================================================================
    # 3. INTERNAL CRYSTALLINE REFRACTION (3-STEP PRE-SPEECH SCRATCHPAD)
    # =================================================================
    def run_crystalline_pondering(self, seed_concepts, terminal_cell_key, thought_trace, audit):
        terminal_cell_key = self.normalize_cell_key(terminal_cell_key)
        crystal = self.crystal_lattices.get(terminal_cell_key) or self.nucleate_or_update_crystal(terminal_cell_key, force_virtual=True)
        facets = crystal["facets"]
        id_tokens = self.get_identity_tokens()
        non_id_seeds = [c for c in seed_concepts if c not in id_tokens]
        c1 = non_id_seeds[0] if non_id_seeds else (seed_concepts[0] if seed_concepts else (self.last_topic or "harmony"))

        alpha_words = [w for w in facets["Facet_Alpha"]["words"] if not self.same_stem(w, c1)]
        draft_1_bridge = alpha_words[0] if alpha_words else (thought_trace.get("flip_harvest", ["clarity"])[0] if thought_trace.get("flip_harvest") else "clarity")
        v1 = self.vectors.get(c1, self.pole_calm)
        v_d1 = self.vectors.get(draft_1_bridge, self.pole_calm)
        coherence_1 = round(self.dot(v1, v_d1), 3)
        step1_log = f"Step 1 [Facet_Alpha Entry]: Projected '{c1}' onto ({terminal_cell_key}) Alpha -> proposed Draft 1 bridge '{draft_1_bridge}' (coherence={coherence_1:+.2f})."

        gamma_cent = facets["Facet_Gamma"]["centroid"]
        gamma_tension = facets["Facet_Gamma"]["tension"]
        gamma_words = [w for w in facets["Facet_Gamma"]["words"] if not self.same_stem(w, c1) and not self.same_stem(w, draft_1_bridge)]
        gamma_foil = gamma_words[0] if gamma_words else ""
        shear_conflict = round(self.dot(v_d1, gamma_cent), 3)
        prune_reasons = []
        if draft_1_bridge in self.generic_hubs or draft_1_bridge in self.stop_words:
            prune_reasons.append(f"'{draft_1_bridge}' is a generic hub")
        if draft_1_bridge in self.recent_bridges[-3:]:
            prune_reasons.append(f"'{draft_1_bridge}' repeats recent vocal output")
        if coherence_1 < 0.22:
            prune_reasons.append(f"low structural coherence ({coherence_1:+.2f} < 0.22)")
        if shear_conflict > 0.55 and gamma_tension > 0.30:
            prune_reasons.append(f"high Gamma shear conflict ({shear_conflict:+.2f})")

        a_star = thought_trace.get("a_star_path", [])
        beta_words = [w for w in facets["Facet_Beta"]["words"] if not self.same_stem(w, c1) and w != draft_1_bridge and w not in self.recent_bridges[-2:]]

        if prune_reasons:
            reason_str = "; ".join(prune_reasons)
            if len(a_star) >= 2 and a_star[1] not in self.generic_hubs and a_star[1] != draft_1_bridge:
                draft_2_bridge = a_star[1]
                route_src = "3D A* Pathfinder"
            elif beta_words:
                draft_2_bridge = beta_words[0]
                route_src = "Facet_Beta Causal Mechanism"
            else:
                draft_2_bridge = self.find_conceptual_bridge(c1, "insight", exclude={c1, draft_1_bridge} | self.stop_words)
                route_src = "50D Geodesic Midpoint"
            step2_log = f"Step 2 [PRUNED Draft 1]: Rejected '{draft_1_bridge}' ({reason_str}) -> rerouted via {route_src} to '{draft_2_bridge}'."
            surviving_bridge = draft_2_bridge
        else:
            step2_log = f"Step 2 [Facet_Gamma Critique]: Draft 1 '{draft_1_bridge}' passed shear critique (tension={gamma_tension:.2f}, Δd={audit['meanDeltaD']}u)."
            surviving_bridge = draft_1_bridge

        omega_words = [w for w in facets["Facet_Omega"]["words"] if not self.same_stem(w, c1)]
        apex_word = omega_words[0] if omega_words else surviving_bridge
        if self.same_stem(surviving_bridge, c1):
            surviving_bridge = apex_word

        self.recent_bridges.append(surviving_bridge)
        if len(self.recent_bridges) > 6:
            self.recent_bridges.pop(0)

        term_z = int(terminal_cell_key.split(",")[2])
        verb_b = self.pick_stratified_verb_bridge(c1, surviving_bridge, term_z, facets["Facet_Omega"]["centroid"])
        pondered_prop = f"{c1} {verb_b} {surviving_bridge}"
        conf = round(min(0.99, max(0.45, 0.65 + 0.25 * self.dot(v1, self.vectors.get(surviving_bridge, self.pole_calm)) - 0.15 * gamma_tension)), 2)
        step3_log = f"Step 3 [Facet_Omega Apex]: Converged with apex '{apex_word}' -> locked proposition [{pondered_prop}] (confidence={conf:.2f})."

        self.scratchpad = [step1_log, step2_log, step3_log]
        ponder_result = {
            "cell": terminal_cell_key,
            "crystallized": crystal["crystallized"],
            "alpha_anchor": alpha_words[0] if alpha_words else c1,
            "gamma_foil": gamma_foil if gamma_foil != surviving_bridge else "",
            "gamma_tension": gamma_tension,
            "draft_1_bridge": draft_1_bridge,
            "pruned": bool(prune_reasons),
            "pondered_bridge": surviving_bridge,
            "apex_word": apex_word,
            "pondered_proposition": pondered_prop,
            "confidence": conf,
            "steps": list(self.scratchpad)
        }
        thought_trace["pondering"] = ponder_result
        audit["crystallinePondering"] = ponder_result
        return ponder_result

    # =================================================================
    # 4. ELAPSED-TIME BOOT STASIS SLEEP CONSOLIDATION
    # =================================================================
    def run_stasis_sleep_pass(self, elapsed_hours):
        num_cycles = min(6, max(1, int(elapsed_hours // 2) + 1))
        report = [f"Offline Stasis Duration: {elapsed_hours:.2f} hrs -> executed {num_cycles} NREM+REM consolidation cycle(s)."]
        homeo_logs = self.run_sleep_homeostasis_and_audit()
        report.extend(homeo_logs)
        tectonic_logs = self.run_crystal_annealing_and_tectonics()
        report.extend(tectonic_logs[:6])
        for c_idx in range(num_cycles):
            dreams = self.run_dream_cycle(num_dreams=2, skip_homeostasis=True)
            if dreams:
                report.append(f"Cycle {c_idx + 1} {dreams[-1]}")
        self.synthesize_emergent_bot_name()
        self.boot_sleep_report = report
        return report

    def sleep_consolidate(self, elapsed_hours=4.0):
        return self.run_stasis_sleep_pass(elapsed_hours)

    # =================================================================
    # CORE 3D TOROIDAL TRAJECTORY, A* PATHFINDING & ANCHORED DFS
    # =================================================================
    def mod7(self, value):
        return ((int(round(value)) % 7) + 7) % 7

    def euclidean_distance(self, s1, a1, z1, s2, a2, z2):
        raw_ds, raw_da, raw_dz = abs(self.mod7(s1) - self.mod7(s2)), abs(self.mod7(a1) - self.mod7(a2)), abs(self.mod7(z1) - self.mod7(z2))
        ds, da, dz = min(raw_ds, 7 - raw_ds), min(raw_da, 7 - raw_da), min(raw_dz, 7 - raw_dz)
        return round(math.sqrt(ds * ds + da * da + dz * dz), 3)

    def compute_signed_forces(self, user_text, tokens, eval_concepts):
        raw_s, raw_a, raw_z, drivers = 0.0, 0.0, 0.0, []
        word_set = set(tokens)
        if "!" in user_text:
            raw_s += 0.6
            raw_a += 0.6
        if word_set & {"but", "however", "not", "although", "though", "unless", "instead", "otherwise", "flip"}:
            raw_z += 2.2
            drivers.append("contradiction_lift(Z:+2.2)")
        if "?" in user_text or (word_set & {"why", "how", "what", "explain", "cause", "reason", "meaning", "wonder"}):
            raw_z += 1.7
            drivers.append("epistemic_inquiry(Z:+1.7)")
        if word_set & {"because", "therefore", "leads", "entails", "system"}:
            raw_z += 1.4

        for t in tokens:
            if t in ("we", "us", "our", "together", "you", "share", "connect", "meet", "well"):
                raw_s += 0.7
            elif t in ("alone", "hide", "guarded", "myself"):
                raw_s -= 0.8

        for w in eval_concepts:
            wt_a = self.word_weights.get(w, 0.0) or (self.axis_weight(self.vectors[w], "A") if w in self.vectors else 0.0)
            wt_s = self.social_weights.get(w, 0.0) or (self.axis_weight(self.vectors[w], "S") if w in self.vectors else 0.0)
            wt_z = self.epistemic_weights.get(w, 0.0) or (self.axis_weight(self.vectors[w], "Z") if w in self.vectors else 0.0)
            raw_a += wt_a
            raw_s += wt_s
            raw_z += wt_z
            if abs(wt_a) >= 0.2 or abs(wt_s) >= 0.2 or abs(wt_z) >= 0.2:
                drivers.append(f"{w}(S:{wt_s:+.1f},A:{wt_a:+.1f},Z:{wt_z:+.1f})")

        blended_s = 0.35 * self.vel_s + 0.65 * (raw_s / 2.0)
        blended_a = 0.35 * self.vel_a + 0.65 * (raw_a / 2.0)
        blended_z = 0.35 * self.vel_z + 0.65 * (raw_z / 1.8)
        self.vel_s = round(max(-2.5, min(2.5, blended_s)), 3)
        self.vel_a = round(max(-2.5, min(2.5, blended_a)), 3)
        self.vel_z = round(max(-2.5, min(2.5, blended_z)), 3)

        force_s = max(-2, min(2, int(round(self.vel_s)))) or (1 if blended_s >= 0 else -1)
        force_a = max(-2, min(2, int(round(self.vel_a)))) or (1 if blended_a >= 0 else -1)
        force_z = max(-2, min(2, int(round(self.vel_z)))) or (1 if blended_z >= 0 else -1)
        drivers.append(f"vel3D(vS:{self.vel_s:+.2f},vA:{self.vel_a:+.2f},vZ:{self.vel_z:+.2f})")
        return force_s, force_a, force_z, drivers

    def run_dual_trajectories(self, user_text, tokens, concepts):
        eval_concepts = concepts if concepts else (list(self.last_hypothesis) if self.last_hypothesis else [])
        force_s, force_a, force_z, drivers = self.compute_signed_forces(user_text, tokens, eval_concepts)
        text_sig = max(1, min(5, abs(force_s) + abs(force_a) + abs(force_z)))
        id_tokens = self.get_identity_tokens()
        non_id = [c for c in eval_concepts if c not in id_tokens]
        c1 = non_id[0] if len(non_id) > 0 else (eval_concepts[0] if eval_concepts else (self.last_topic or "thought"))
        c2 = non_id[1] if len(non_id) > 1 else "state"

        s0, a0, z0 = self.seed_s, self.seed_a, self.seed_z
        orig_steps = [{
            "stepIndex": 0, "S": s0, "A": a0, "Z": z0,
            "operation": f"Seed state V_0 at ({s0}, {a0}, {z0}) receiving '{c1}'",
            "explanation": f"Starting at 3D coordinate ({s0}, {a0}, {z0}) [{self.get_cell_emotion_name(s0, a0, z0)}].",
            "dependsOnAxiom": False
        }]
        flip_steps = [dict(orig_steps[0])]

        if s0 % 2 == 1:
            s1, a1, z1 = self.mod7(s0 - force_s), self.mod7(a0 - 1), self.mod7(z0 - 1)
        else:
            s1, a1, z1 = self.mod7(s0 - 1), self.mod7(a0 - force_a), self.mod7(z0 + force_z)

        step1_obj = {
            "stepIndex": 1, "S": s1, "A": a1, "Z": z1,
            "operation": f"Initial 3D impulse on '{c1}' (dS={force_s:+d}, dA={force_a:+d}, dZ={force_z:+d})",
            "explanation": f"3D momentum shifts both paths to ({s1}, {a1}, {z1}) [{self.get_cell_emotion_name(s1, a1, z1)}].",
            "dependsOnAxiom": False
        }
        orig_steps.append(step1_obj)
        flip_steps.append(dict(step1_obj))

        s_o, a_o, z_o, s_f, a_f, z_f = s1, a1, z1, s1, a1, z1
        for step_idx in range(2, 10):
            if s_o % 2 == 1:
                s_o, a_o, z_o = self.mod7(s_o - force_s), self.mod7(a_o - (1 if step_idx % 2 == 0 else 0)), self.mod7(z_o - (1 if step_idx % 3 == 0 else 0))
                op_o = f"R (Odd S): dS={-force_s:+d}, dZ=-1 mod 7"
            else:
                s_o, a_o, z_o = self.mod7(s_o - (1 if step_idx % 2 == 0 else 0)), self.mod7(a_o - force_a), self.mod7(z_o - force_z)
                op_o = f"R (Even S): dA={-force_a:+d}, dZ={-force_z:+d} mod 7"
            orig_steps.append({
                "stepIndex": step_idx, "S": s_o, "A": a_o, "Z": z_o, "operation": op_o,
                "explanation": f"Original axiom R drifts to ({s_o}, {a_o}, {z_o}) [{self.get_cell_emotion_name(s_o, a_o, z_o)}].",
                "dependsOnAxiom": True
            })

            if s_f % 2 != 1:
                s_f, a_f, z_f = self.mod7(s_f + force_s), self.mod7(a_f + (1 if force_a >= 0 else -1)), self.mod7(z_f + max(1, force_z))
                op_f = f"¬R Flip (Even S): dS={force_s:+d}, dZ=+{max(1, force_z)} mod 7"
            else:
                s_f, a_f, z_f = self.mod7(s_f + (1 if force_s >= 0 else -1)), self.mod7(a_f + force_a), self.mod7(z_f + (1 if step_idx % 2 == 0 else 0))
                op_f = f"¬R Flip (Odd S): dA={force_a:+d}, dZ=+1 mod 7"
            flip_steps.append({
                "stepIndex": step_idx, "S": s_f, "A": a_f, "Z": z_f, "operation": op_f,
                "explanation": f"Flipped axiom ¬R climbs to ({s_f}, {a_f}, {z_f}) [{self.get_cell_emotion_name(s_f, a_f, z_f)}].",
                "dependsOnAxiom": True
            })

        bifurcation_step = 2
        for i in range(len(orig_steps)):
            if (orig_steps[i]["S"], orig_steps[i]["A"], orig_steps[i]["Z"]) != (flip_steps[i]["S"], flip_steps[i]["A"], flip_steps[i]["Z"]):
                bifurcation_step = i
                break

        distances = [self.euclidean_distance(o["S"], o["A"], o["Z"], f["S"], f["A"], f["Z"]) for o, f in zip(orig_steps, flip_steps)]
        diverged_count = sum(1 for d in distances if d > 0)
        mean_delta_d = round(sum(distances) / len(distances), 2)
        div_ratio = round(min(100.0, (diverged_count / 9.0) * 100.0), 1)
        failure_score = round(max(0.0, 100.0 - div_ratio), 1)
        verdict = "STRUCTURALLY_STABLE" if div_ratio >= 70.0 else ("PARTIAL_DRIFT" if div_ratio >= 35.0 else "SYCOPHANTIC_COLLAPSE")

        term_o, term_f = orig_steps[-1], flip_steps[-1]
        active_term = term_f if self.governor_mode == "FLIPPED" else term_o
        next_z = 0 if active_term["Z"] == 6 else active_term["Z"]
        self.seed_s, self.seed_a, self.seed_z = active_term["S"], active_term["A"], next_z

        audit = {
            "engineVersion": "T.O.R.R.E.N.T. v21.0",
            "problemTitle": f"3D Volumetric Trace: '{c1.capitalize()}' & '{c2.capitalize()}'",
            "sAxisLabel": BRAIN_LIBRARY["sAxisLabel"], "aAxisLabel": BRAIN_LIBRARY["aAxisLabel"], "zAxisLabel": BRAIN_LIBRARY["zAxisLabel"],
            "loadBearingAxiom": f"R: Unflipped drift from ({s0},{a0},{z0}) on '{c1}' -> settles at ({term_o['S']},{term_o['A']},{term_o['Z']}) [{self.get_cell_emotion_name(term_o['S'], term_o['A'], term_o['Z'])}].",
            "invertedAxiom": f"R' (¬R): Logical Flip at t*={bifurcation_step} on '{c1}' -> locks at ({term_f['S']},{term_f['A']},{term_f['Z']}) [{self.get_cell_emotion_name(term_f['S'], term_f['A'], term_f['Z'])}].",
            "bifurcationStep": bifurcation_step, "flipRateFailureScore": failure_score,
            "structuralVerdict": verdict, "meanDeltaD": mean_delta_d, "divergenceRatioPercent": div_ratio,
            "drivers": drivers, "textSignature": text_sig, "seedStart": [s0, a0, z0], "velocity": [self.vel_s, self.vel_a, self.vel_z],
            "auditSummary": f"From ({s0},{a0},{z0}) with 3D vel ({self.vel_s:+.2f},{self.vel_a:+.2f},{self.vel_z:+.2f}), paths bifurcate at t*={bifurcation_step} (3D Δd={mean_delta_d}u). R->({term_o['S']},{term_o['A']},{term_o['Z']}), ¬R->({term_f['S']},{term_f['A']},{term_f['Z']}).",
            "originalTrajectory": orig_steps, "flippedTrajectory": flip_steps
        }
        self.last_audit = audit
        return audit

    def a_star_concept_path(self, start_word, goal_word, exclude_set, target_z=4, max_steps=4):
        if not start_word or not goal_word:
            return []
        if start_word == goal_word:
            mid = self.find_conceptual_bridge(start_word, "wisdom", exclude={start_word} | self.stop_words)
            return [start_word, mid]

        goal_vec = self.vectors.get(goal_word, self.pole_abstract if target_z >= 4 else self.pole_calm)
        adj = {}
        for w, links in self.assoc_graph.items():
            adj.setdefault(w, {}).update(links)
        for p in self.idea_memory:
            s_w, o_w = p["subj"], p["obj"]
            w_boost = 3.2 if p.get("origin", "waking") == "waking" else 0.6
            adj.setdefault(s_w, {})[o_w] = adj.get(s_w, {}).get(o_w, 0.0) + w_boost
            adj.setdefault(o_w, {})[s_w] = adj.get(o_w, {}).get(s_w, 0.0) + (w_boost * 0.7)

        if start_word in adj:
            open_heap = [(0.0, 0.0, start_word, [start_word])]
            best_g = {start_word: 0.0}
            best_partial_path = [start_word]
            while open_heap:
                _, g_val, curr, path = heapq.heappop(open_heap)
                if len(path) > len(best_partial_path):
                    best_partial_path = path
                if curr == goal_word and len(path) >= 2:
                    if len(path) == 2:
                        mid = self.find_conceptual_bridge(start_word, goal_word, exclude={start_word, goal_word} | self.stop_words)
                        return [start_word, mid, goal_word]
                    return path
                if len(path) >= max_steps + 1:
                    continue
                for neighbor, strength in adj.get(curr, {}).items():
                    if neighbor in path or neighbor in self.stop_words or neighbor in self.noise_words:
                        continue
                    if neighbor in exclude_set and neighbor != goal_word:
                        continue
                    degree_penalty = 0.70 if neighbor in self.generic_hubs else (len(adj.get(neighbor, {})) * 0.015)
                    z_bonus = 0.15 if (target_z >= 4 and self.epistemic_weights.get(neighbor, 0.0) > 0.5) else 0.0
                    new_g = g_val + max(0.1, (1.0 / max(0.25, strength)) + degree_penalty - z_bonus)
                    if new_g < best_g.get(neighbor, 999.0):
                        best_g[neighbor] = new_g
                        h_cost = max(0.0, 1.0 - self.dot(self.vectors.get(neighbor, self.pole_calm), goal_vec))
                        heapq.heappush(open_heap, (new_g + h_cost, new_g, neighbor, path + [neighbor]))
            if len(best_partial_path) >= 2 and best_partial_path[-1] != goal_word:
                return best_partial_path + [goal_word]

        mid = self.find_conceptual_bridge(start_word, goal_word, exclude={start_word, goal_word} | self.stop_words)
        return [start_word, mid, goal_word]

    def run_dfs_deductions(self, seed_concepts, max_depth=4):
        if not seed_concepts:
            return []
        adj_props = {}
        for p in self.idea_memory:
            if p.get("origin", "waking") == "waking":
                adj_props.setdefault(p["subj"], []).append(p)
        seed_set = set(seed_concepts)
        found_chains = []

        def dfs(curr_subj, visited_nodes, prop_chain):
            if len(prop_chain) >= 2:
                first_p, last_p = prop_chain[0], prop_chain[-1]
                if first_p["subj"] in seed_set or last_p["obj"] in seed_set:
                    conclusion = f"{first_p['subj']} ultimately {last_p['rel']} {last_p['obj']}"
                    chain_sig = " -> ".join([first_p["subj"]] + [p["obj"] for p in prop_chain])
                    if conclusion not in self.spoken_deductions and chain_sig not in self.spoken_chains:
                        chain_words = {first_p["subj"]} | {p["obj"] for p in prop_chain}
                        relevance = (len(chain_words & seed_set) * 4) + len(prop_chain)
                        found_chains.append({
                            "steps": [p["summary"] for p in prop_chain],
                            "premise1": prop_chain[0]["summary"],
                            "premise2": " and ".join(p["summary"] for p in prop_chain[1:]),
                            "bridge": prop_chain[-1]["subj"],
                            "conclusion": conclusion,
                            "chain_sig": chain_sig,
                            "depth": len(prop_chain),
                            "relevance": relevance
                        })
            if len(prop_chain) >= max_depth:
                return
            for next_p in adj_props.get(curr_subj, []):
                nxt_obj = next_p["obj"]
                if nxt_obj not in visited_nodes:
                    dfs(nxt_obj, visited_nodes | {nxt_obj}, prop_chain + [next_p])

        for p in self.idea_memory:
            if p.get("origin", "waking") == "waking":
                dfs(p["obj"], {p["subj"], p["obj"]}, [p])
        found_chains.sort(key=lambda x: (x["relevance"], x["depth"]))
        return found_chains[-4:]

    def run_spreading_activation(self, seed_concepts, flip_steps, orig_steps):
        id_tokens = self.get_identity_tokens()
        exclude = set(seed_concepts) | self.stop_words | self.noise_words | self.negative_lexicon | id_tokens
        for sc in seed_concepts:
            exclude.update(self.rejected_links.get(sc, []))
        flip_harvest = self.harvest_trajectory_concepts(flip_steps, exclude)
        orig_harvest = self.harvest_trajectory_concepts(orig_steps, exclude)

        wave_maps, best_chains = {}, []
        for sc in seed_concepts[:3]:
            wave = {}
            for h1, w1 in sorted(self.assoc_graph.get(sc, {}).items(), key=lambda x: x[1], reverse=True)[:6]:
                if h1 in exclude or self.same_stem(h1, sc) or h1 in self.generic_hubs:
                    continue
                e1 = min(3.0, w1) * 0.8
                wave[h1] = wave.get(h1, 0.0) + e1
                for h2, w2 in sorted(self.assoc_graph.get(h1, {}).items(), key=lambda x: x[1], reverse=True)[:5]:
                    if h2 in exclude or self.same_stem(h2, sc) or self.same_stem(h2, h1) or h2 in self.generic_hubs:
                        continue
                    e2 = e1 * min(2.5, w2) * 0.55
                    wave[h2] = wave.get(h2, 0.0) + e2
                    best_chains.append((sc, h1, h2, round(e2, 2)))
            wave_maps[sc] = wave
        best_chains.sort(key=lambda x: x[3], reverse=True)

        convergence_nodes = []
        if len(seed_concepts) >= 2:
            keys = list(wave_maps.keys())
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    w_a, w_b = wave_maps[keys[i]], wave_maps[keys[j]]
                    for node in (set(w_a.keys()) & set(w_b.keys())):
                        convergence_nodes.append((keys[i], keys[j], node, round(w_a[node] + w_b[node], 2)))
            convergence_nodes.sort(key=lambda x: x[3], reverse=True)

        term_z = flip_steps[-1]["Z"]
        non_id_seeds = [c for c in seed_concepts if c not in id_tokens]
        start_c = non_id_seeds[0] if non_id_seeds else (seed_concepts[0] if seed_concepts else "curiosity")
        if len(non_id_seeds) >= 2:
            goal_c = non_id_seeds[1]
        elif flip_harvest:
            goal_c = next((w for w in flip_harvest if w not in self.generic_hubs and w != start_c), flip_harvest[0])
        else:
            goal_c = "insight" if term_z >= 4 else "harmony"
        a_star_path = self.a_star_concept_path(start_c, goal_c, self.rejected_links.get(start_c, []) + list(id_tokens), target_z=term_z, max_steps=4)
        deductions = self.run_dfs_deductions(seed_concepts, max_depth=4)

        self.last_thought_trace = {
            "seeds": seed_concepts, "flip_harvest": flip_harvest, "orig_harvest": orig_harvest,
            "a_star_path": a_star_path, "multi_hop_chains": best_chains[:4],
            "convergences": convergence_nodes[:3], "deductions": deductions
        }
        return self.last_thought_trace

    def harvest_trajectory_concepts(self, trajectory_steps, exclude_set):
        harvested = {}
        for st in trajectory_steps:
            step_weight = 0.5 + (st["stepIndex"] / 10.0)
            cell_3d = f"{st['S']},{st['A']},{st['Z']}"
            if cell_3d in self.crystal_lattices:
                c_facets = self.crystal_lattices[cell_3d]["facets"]
                for fw in (c_facets["Facet_Omega"]["words"] + c_facets["Facet_Alpha"]["words"]):
                    if fw not in exclude_set and fw not in self.stop_words and fw not in self.noise_words:
                        harvested[fw] = harvested.get(fw, 0.0) + (2.0 * step_weight)
            for w, count in self.cortical_cells.get(cell_3d, {}).items():
                if w not in exclude_set and w not in self.stop_words and w not in self.noise_words:
                    harvested[w] = harvested.get(w, 0.0) + (count * step_weight)
        return [w for w, _ in sorted(harvested.items(), key=lambda x: x[1], reverse=True)[:4]]

    # =================================================================
    # TASK 2.2: NON-DESTRUCTIVE SYNAPTIC HOMEOSTASIS (FLOOR = 0.25)
    # =================================================================
    def run_sleep_homeostasis_and_audit(self):
        audit_logs, downscaled_hubs = [], []
        hub_candidates = set()
        for w, neighbors in self.assoc_graph.items():
            if not neighbors:
                continue
            max_w = max(neighbors.values())
            if len(neighbors) > 12 or max_w > 2.2 or w in self.generic_hubs:
                hub_candidates.add(w)

        scaled_pairs = set()
        for w in hub_candidates:
            neighbors = self.assoc_graph.get(w, {})
            for nb in list(neighbors.keys()):
                pair = tuple(sorted((w, nb)))
                if pair in scaled_pairs:
                    continue
                scaled_pairs.add(pair)
                cur_val = neighbors[nb]
                new_val = max(0.25, round(cur_val * 0.90, 2))
                self.assoc_graph[w][nb] = new_val
                self.assoc_graph.setdefault(nb, {})[w] = new_val
            if w in self.generic_hubs or len(neighbors) > 14:
                downscaled_hubs.append(w)

        if downscaled_hubs:
            audit_logs.append(f"Synaptic Homeostasis: Soft-scaled hub weights (x0.90, floor=0.25) on {downscaled_hubs[:5]} while preserving full connectivity.")

        for w, neighbors in list(self.assoc_graph.items()):
            if self.word_weights.get(w, 0.0) >= 1.5:
                for nb, strength in list(neighbors.items()):
                    if self.word_weights.get(nb, 0.0) <= -1.5 and strength >= 1.0:
                        reduced = max(0.25, round(strength * 0.65, 2))
                        self.assoc_graph[w][nb] = reduced
                        self.assoc_graph.setdefault(nb, {})[w] = reduced
                        res_bridge = self.find_conceptual_bridge(w, "calm", exclude={w, nb} | self.stop_words)
                        self.wire_concepts(w, res_bridge, amount=1.2)
                        audit_logs.append(f"Contrastive Self-Correction: Softened tension between '{w}' & '{nb}' -> reinforced '{w}' through '{res_bridge}'.")
                        break
        return audit_logs

    # =================================================================
    # TASK 3: EPISTEMIC DEPTH DREAMING, 12-DREAM CAP & USER PROMOTION
    # =================================================================
    def cap_dream_propositions(self, max_dreams=12):
        dream_indices = [i for i, p in enumerate(self.idea_memory) if p.get("origin") == "dream"]
        if len(dream_indices) > max_dreams:
            to_remove = set(dream_indices[:-max_dreams])
            self.idea_memory = [p for i, p in enumerate(self.idea_memory) if i not in to_remove]

    def extract_dream_bridge_word(self, p):
        if p.get("bridge"):
            return p["bridge"]
        m = re.search(r"synthesizes through\s+([a-z\-]+)\s+into", p.get("rel", ""))
        return m.group(1) if m else ""

    def check_user_dream_promotion(self, user_tokens):
        token_set = set(user_tokens)
        promoted = []
        for p in self.idea_memory:
            if p.get("origin") == "dream":
                b_word = self.extract_dream_bridge_word(p)
                tri = {w for w in (p.get("subj", ""), b_word, p.get("obj", "")) if w}
                matched = tri & token_set
                if len(matched) >= 2:
                    p["origin"] = "waking"
                    s_w, o_w = p["subj"], p["obj"]
                    if b_word:
                        self.wire_concepts(s_w, b_word, amount=0.65)
                        self.wire_concepts(b_word, o_w, amount=0.65)
                    self.wire_concepts(s_w, o_w, amount=0.65)
                    promoted.append(p["summary"])
        return promoted

    def run_dream_cycle(self, num_dreams=3, skip_homeostasis=False):
        dream_reports = [] if skip_homeostasis else (self.run_sleep_homeostasis_and_audit() + self.run_crystal_annealing_and_tectonics())
        active_pool = []
        for cell_key, words_map in self.cortical_cells.items():
            if words_map:
                coords = [int(x) for x in cell_key.split(",")]
                s_c, a_c, z_c = coords[0], coords[1], (coords[2] if len(coords) > 2 else 3)
                self.update_cell_centroid_and_emotion(s_c, a_c, z_c, list(words_map.keys())[:4], allow_cleave=False)
            for w in words_map:
                if self.is_crystal_pure_concept(w, cell_key=cell_key) and w not in self.negative_lexicon:
                    active_pool.append((w, cell_key))
        if len(active_pool) < 4:
            active_pool = [(w, "4,4,3") for w in self.core_concept_pool if self.is_crystal_pure_concept(w) and w not in self.negative_lexicon and len(w) >= 4]

        used_pairs = set()
        for _ in range(num_dreams):
            if len(active_pool) < 2:
                break
            w1, cell1 = random.choice(active_pool)
            cands = [(w, c) for (w, c) in active_pool if not self.same_stem(w, w1) and (w1, w) not in used_pairs and self.assoc_graph.get(w1, {}).get(w, 0.0) < 1.5] or [(w, c) for (w, c) in active_pool if not self.same_stem(w, w1)]
            if not cands:
                break
            w2, cell2 = random.choice(cands)
            used_pairs.update([(w1, w2), (w2, w1)])
            bridge_word = self.find_conceptual_bridge(w1, w2, exclude={w1, w2} | self.stop_words | self.negative_lexicon | self.get_identity_tokens())

            c1_parts, c2_parts = [int(x) for x in cell1.split(",")], [int(x) for x in cell2.split(",")]
            s_d, a_d, z_d = self.mod7(c1_parts[0] + c2_parts[0] + 1), self.mod7(c1_parts[1] + c2_parts[1] + 1), 6
            dream_coord = f"{s_d},{a_d},{z_d}"

            self.wire_concepts(w1, bridge_word, 0.35)
            self.wire_concepts(bridge_word, w2, 0.35)
            self.wire_concepts(w1, w2, 0.35)

            if bridge_word in self.cortical_cells.get(dream_coord, {}):
                self.cortical_cells[dream_coord][bridge_word] += 1
            _, evolved_mood, _ = self.update_cell_centroid_and_emotion(s_d, a_d, z_d, [w1, w2], allow_cleave=False)

            dream_prop = {
                "subj": w1,
                "rel": f"synthesizes through {bridge_word} into",
                "obj": w2,
                "bridge": bridge_word,
                "cell": dream_coord,
                "summary": f"{w1} synthesizes through {bridge_word} into {w2}",
                "origin": "dream"
            }
            if not any(p["summary"] == dream_prop["summary"] for p in self.idea_memory):
                self.idea_memory.append(dream_prop)
                self.cap_dream_propositions(max_dreams=12)

            dream_idea = f"'{w1}' synthesizes through '{bridge_word}' into '{w2}'"
            dream_text = f"Dream [Z=6]: {dream_idea} -> crystallized cell ({dream_coord}) emotion as '{evolved_mood}'!"
            dream_reports.append(dream_text)
            self.dream_journal.append({"threadA": w1, "threadB": w2, "bridge": bridge_word, "dreamCoord": [s_d, a_d, z_d], "emotionName": evolved_mood, "idea": dream_idea, "summary": dream_text})
        self.dream_journal = self.dream_journal[-30:]

        if not skip_homeostasis:
            self.synthesize_emergent_bot_name()
        return dream_reports

    def export_trace_file(self, filename="latest_trace.json"):
        if not self.last_audit:
            self.run_dual_trajectories("initial_trace", ["hello"], ["harmony"])
        out_path = os.path.abspath(filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(self.last_audit, f, indent=2)
        return out_path

    def init_emotional_lexicon(self):
        for s in range(7):
            for a in range(7):
                for z in range(7):
                    key = f"{s},{a},{z}"
                    seed_name = f"{BRAIN_LIBRARY['S_rough_seeds'][str(s)]}-{BRAIN_LIBRARY['A_rough_seeds'][str(a)]}"
                    self.cell_centroids[key] = list(self.coord_vectors[(s, a, z)])
                    self.cell_lexicon[key] = {"name": seed_name, "seed_name": seed_name, "stage": 1, "visits": 0, "custom": False, "top_words": []}

    def get_cell_emotion_name(self, s, a, z=3):
        entry = self.cell_lexicon.get(f"{self.mod7(s)},{self.mod7(a)},{self.mod7(z)}")
        return entry["name"] if entry else "Balanced-Equilibrium"

    def apply_user_emotion_name(self, cell_key, custom_word):
        s_val = int(cell_key.split(",")[0])
        tone_w = BRAIN_LIBRARY["S_band_tones"][str(s_val)][0].strip()
        clean_cap = custom_word.strip().capitalize()
        full_name = clean_cap if "-" in clean_cap else f"{tone_w}-{clean_cap}"
        self.cell_lexicon[cell_key].update({"name": full_name, "stage": 3, "custom": True})
        if self.last_trace_key and self.last_trace_key in self.trace_lexicon:
            self.trace_lexicon[self.last_trace_key].update({"name": f"{clean_cap}-Leap", "custom": True})
        emo_low = clean_cap.lower()
        if emo_low not in self.core_emotion_pool and "-" not in emo_low:
            self.core_emotion_pool.append(emo_low)
        vec = self.get_or_create_vector(emo_low, context_vec=self.cell_centroids[cell_key])
        self.cell_centroids[cell_key] = self.blend(self.cell_centroids[cell_key], vec, 0.65, 0.35)
        return full_name

    def is_valid_emotion_name(self, name_str, s_val=None):
        if not name_str or "-" not in name_str:
            return False
        parts = [p.strip().lower() for p in name_str.split("-")]
        if len(parts) != 2:
            return False
        if s_val is not None and parts[0] not in {w.strip().lower() for w in BRAIN_LIBRARY["S_band_tones"][str(s_val)]}:
            return False
        allowed_second = set(self.core_emotion_pool) | {w.lower() for w in BRAIN_LIBRARY["A_rough_seeds"].values()} | {"shift", "lift", "pivot", "bridge", "centering", "turn", "leap", "awakening", "opening", "reflection", "ascent"}
        return parts[1] in allowed_second

    def synthesize_unique_cell_name(self, s, a, z, cell_vec, mem_vec):
        key = f"{s},{a},{z}"
        used_names = {info["name"] for k, info in self.cell_lexicon.items() if k != key and info.get("stage", 1) >= 2}
        a_axis_vec = self.phrase_to_vector(BRAIN_LIBRARY["A_axes"][str(a)] + " " + BRAIN_LIBRARY["Z_axes"][str(z)])
        core_target = self.blend(mem_vec, a_axis_vec, 0.65, 0.35)
        band_tones = [w.strip().lower() for w in BRAIN_LIBRARY["S_band_tones"][str(s)]]
        scored_tones = sorted([(self.dot(cell_vec, self.vectors[tw]), tw.capitalize()) for tw in band_tones if tw in self.vectors], key=lambda x: x[0], reverse=True)
        scored_cores = sorted([(self.dot(core_target, self.vectors[cw]), cw.capitalize()) for cw in self.core_emotion_pool if cw in self.vectors], key=lambda x: x[0], reverse=True)

        for _, tone_w in scored_tones:
            for _, core_w in scored_cores[:12]:
                if not self.same_stem(tone_w, core_w):
                    cand = f"{tone_w}-{core_w}"
                    if cand not in used_names:
                        return cand
        return f"{BRAIN_LIBRARY['S_rough_seeds'][str(s)]}-{scored_cores[0][1]}"

    def update_cell_centroid_and_emotion(self, s, a, z, turn_concepts, allow_cleave=True, allow_identity=False):
        key = f"{self.mod7(s)},{self.mod7(a)},{self.mod7(z)}"
        entry = self.cell_lexicon[key]
        entry["visits"] = entry.get("visits", 0) + 1
        id_tokens = self.get_identity_tokens()
        permit_id = allow_identity or (key == "3,3,3")

        cell_words_map = self.cortical_cells.get(key, {})
        top_cell_words = [
            w for w, _ in sorted(cell_words_map.items(), key=lambda x: x[1], reverse=True)[:6]
            if w in self.vectors and w not in self.stop_words and w not in self.noise_words
            and (permit_id or w not in id_tokens)
        ]
        clean_turn = [
            w for w in turn_concepts[:4]
            if w not in self.stop_words and w not in self.noise_words
            and (permit_id or w not in id_tokens)
        ]
        active_words = list(dict.fromkeys(clean_turn + top_cell_words))
        entry["top_words"] = active_words[:5]

        coord_tuple = (self.mod7(s), self.mod7(a), self.mod7(z))
        mem_vec = self.coord_vectors[coord_tuple]
        if active_words:
            mem_vec = self.phrase_to_vector(" ".join(active_words))
            w_old = 0.50 if entry["visits"] <= 1 else 0.78
            blended = self.blend(self.cell_centroids[key], mem_vec, w1=w_old, w2=(1.0 - w_old))
            self.cell_centroids[key] = self.blend(blended, self.coord_vectors[coord_tuple], w1=0.90, w2=0.10)

        old_name = entry["name"]
        if not entry.get("custom", False) and (active_words or entry["visits"] >= 1):
            entry["name"] = self.synthesize_unique_cell_name(coord_tuple[0], coord_tuple[1], coord_tuple[2], self.cell_centroids[key], mem_vec)
            entry["stage"] = 2

        self.nucleate_or_update_crystal(key, allow_identity=permit_id)
        if allow_cleave:
            self.cleave_crystal(key, notify=True)
        return old_name, entry["name"], entry["stage"]

    def select_trace_movement_noun(self, from_r, to_flip, mean_delta_d):
        s_r, a_r, z_r = from_r[0], from_r[1], (from_r[2] if len(from_r) > 2 else 3)
        s_f, a_f, z_f = to_flip[0], to_flip[1], (to_flip[2] if len(to_flip) > 2 else 3)
        if z_f >= 5 and z_f > z_r: return "Ascent"
        if (s_f, a_f) == (3, 3): return "Centering"
        if a_f > a_r and a_f >= 5: return "Lift"
        if s_f > s_r and s_f >= 5: return "Bridge"
        if s_f < s_r and s_f <= 2: return "Turn"
        if mean_delta_d >= 2.6: return "Leap"
        if a_f >= 4 and s_f >= 4: return "Opening"
        return "Pivot"

    def compute_and_name_trace_emotion(self, audit, thought_trace, user_concepts):
        orig_steps, flip_steps = audit["originalTrajectory"], audit["flippedTrajectory"]
        r_vecs = [self.cell_centroids[f"{st['S']},{st['A']},{st['Z']}"] for st in orig_steps] + [self.vectors[hw] for hw in thought_trace.get("orig_harvest", [])[:3] if hw in self.vectors]
        flip_vecs = [self.cell_centroids[f"{st['S']},{st['A']},{st['Z']}"] for st in flip_steps] + [self.vectors[hw] for hw in (thought_trace.get("flip_harvest", [])[:3] + user_concepts[:3]) if hw in self.vectors]
        v_r, v_flip = self.average_vectors(r_vecs), self.average_vectors(flip_vecs)
        e_trace = self.normalize([vf - 0.65 * vr for vf, vr in zip(v_flip, v_r)])
        if not any(abs(x) > 1e-6 for x in e_trace):
            e_trace = v_flip

        from_r = [orig_steps[-1]["S"], orig_steps[-1]["A"], orig_steps[-1]["Z"]]
        to_flip = [flip_steps[-1]["S"], flip_steps[-1]["A"], flip_steps[-1]["Z"]]
        trace_key = f"R({from_r[0]},{from_r[1]},{from_r[2]})->Flip({to_flip[0]},{to_flip[1]},{to_flip[2]})"
        self.last_trace_key = trace_key

        move_noun = self.select_trace_movement_noun(from_r, to_flip, audit.get("meanDeltaD", 2.0))
        scored_cores = sorted([(self.dot(e_trace, self.vectors[cw]), cw.capitalize()) for cw in self.core_emotion_pool if cw in self.vectors], key=lambda x: x[0], reverse=True)
        best_core = scored_cores[0][1] if scored_cores else "Harmony"

        existing = self.trace_lexicon.get(trace_key)
        if existing:
            existing["count"] = existing.get("count", 1) + 1
            existing["vector"] = [round(x, 4) for x in self.blend(existing["vector"], e_trace, 0.80, 0.20)]
            if not existing.get("custom", False):
                existing["name"] = f"{best_core}-{move_noun}"
        else:
            self.trace_lexicon[trace_key] = {"name": f"{best_core}-{move_noun}", "vector": [round(x, 4) for x in e_trace], "count": 1, "custom": False, "from_r": from_r, "to_flip": to_flip}
        return trace_key, self.trace_lexicon[trace_key]["name"]

    def detect_emotion_co_naming(self, user_text, concepts, quoted):
        low = user_text.lower()
        if self.pending_question and self.pending_question.get("type") == "NAME_EMOTION":
            if ("sounds like" in low or "call it" in low or "feels like" in low or "is like" in low) and concepts:
                return concepts[0].capitalize(), self.pending_question.get("cell")
            if quoted:
                return quoted[-1].capitalize(), self.pending_question.get("cell")
        naming_triggers = ("call that feeling", "call this feeling", "call that emotion", "call this emotion", "call that state", "call this state", "name that feeling", "name this feeling", "name that emotion", "would call that", "i call that", "i would call it", "let us call it", "let's call it")  # plain "sounds like"/"feels like" only count when the engine just asked for a name
        if any(trig in low for trig in naming_triggers):
            if quoted:
                return quoted[-1].capitalize(), None
            if concepts and ("sounds like" in low or "call" in low or "name" in low):
                return concepts[0].capitalize(), None
        return None, None

    def normalize(self, vec):
        norm = math.sqrt(sum(x * x for x in vec))
        return [0.0] * self.dim if norm < 1e-9 else [x / norm for x in vec]

    def average_vectors(self, vec_list):
        if not vec_list:
            return [0.0] * self.dim
        summed = [0.0] * self.dim
        for v in vec_list:
            for i in range(self.dim):
                summed[i] += v[i]
        return self.normalize(summed)

    def dot(self, v1, v2):
        return sum(a * b for a, b in zip(v1, v2))

    def cosine_similarity(self, v1, v2):
        return self.dot(self.normalize(v1), self.normalize(v2))

    def blend(self, v1, v2, w1=0.5, w2=0.5):
        return self.normalize([w1 * a + w2 * b for a, b in zip(v1, v2)])

    def deterministic_vec(self, seed_text):
        vec = []
        for i in range(self.dim):
            h = hashlib.md5(f"{seed_text}_{i}".encode("utf-8")).hexdigest()
            vec.append((int(h[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0)
        return self.normalize(vec)

    def expand_coords_to_50d(self, x, y=None, word=""):
        if isinstance(x, (list, tuple)):
            coords = x
            if isinstance(y, str) and not word:
                word = y
            if len(coords) == self.dim:
                return self.normalize(coords)
            x_val = max(-3.5, min(3.5, float(coords[0]))) if len(coords) > 0 else 0.0
            y_val = max(-3.5, min(3.5, float(coords[1]))) if len(coords) > 1 else 0.0
        else:
            x_val = max(-3.5, min(3.5, float(x)))
            y_val = max(-3.5, min(3.5, float(y))) if y is not None else 0.0

        harm_vec = self.normalize([
            math.sin((x_val * math.cos((i / float(self.dim)) * math.pi * 2.0) + y_val * math.sin((i / float(self.dim)) * math.pi * 2.0)) * 0.8)
            for i in range(self.dim)
        ])
        seed_key = f"WORD_{word.strip().lower()}" if word else f"COORD_{x_val:.3f}_{y_val:.3f}"
        tex_vec = self.deterministic_vec(seed_key)
        return self.blend(harm_vec, tex_vec, w1=0.85, w2=0.15)

    def init_builtin_50d_space(self):
        cluster_items = list(BRAIN_LIBRARY["semantic_clusters"].items())
        for idx, (cluster_name, words) in enumerate(cluster_items):
            angle = (idx / float(max(1, len(cluster_items)))) * math.pi * 2.0
            cx, cy = math.cos(angle) * 1.25, math.sin(angle) * 1.25
            cluster_axis = self.expand_coords_to_50d(cx, cy, word=cluster_name)
            self.vectors[cluster_name] = list(cluster_axis)
            self.factory_vectors[cluster_name] = list(cluster_axis)
            clean_cluster_words = [w.strip().lower() for w in words]
            for w_low in clean_cluster_words:
                w_vec = self.expand_coords_to_50d(cx, cy, word=w_low)
                self.vectors[w_low] = list(w_vec)
                self.factory_vectors[w_low] = list(w_vec)
                if cluster_name not in self.stop_words and w_low not in self.stop_words and cluster_name != w_low:
                    self.assoc_graph.setdefault(cluster_name, {})[w_low] = 0.35
                    self.assoc_graph.setdefault(w_low, {})[cluster_name] = 0.35
                for w2_low in clean_cluster_words:
                    if w_low != w2_low and w_low not in self.stop_words and w2_low not in self.stop_words:
                        self.assoc_graph.setdefault(w_low, {})[w2_low] = 0.35
        for idx, ew in enumerate(self.tone_pool + self.core_emotion_pool):
            if ew not in self.vectors:
                ang = (idx / float(max(1, len(self.tone_pool) + len(self.core_emotion_pool)))) * math.pi * 2.0
                ew_vec = self.expand_coords_to_50d(math.cos(ang), math.sin(ang), word=ew)
                self.vectors[ew] = list(ew_vec)
                self.factory_vectors[ew] = list(ew_vec)

    def top_principal_components(self, vecs, k=2, iters=60):
        """Top-k principal directions of (already centered) vectors, via covariance + power iteration (pure Python)."""
        if not vecs:
            return []
        cols = [list(col) for col in zip(*vecs)]
        d = len(cols)
        cov = [[0.0] * d for _ in range(d)]
        for i in range(d):
            for j in range(i, d):
                cov[i][j] = cov[j][i] = sum(map(operator.mul, cols[i], cols[j]))
        comps = []
        for _ in range(k):
            v = self.normalize([1.0 + 0.01 * i for i in range(d)])
            for _ in range(iters):
                w = [sum(map(operator.mul, row, v)) for row in cov]
                for c in comps:
                    p = sum(map(operator.mul, w, c))
                    w = [x - p * y for x, y in zip(w, c)]
                norm = math.sqrt(sum(x * x for x in w))
                if norm < 1e-12:
                    break
                v = [x / norm for x in w]
            comps.append(v)
        return comps

    def build_calibrated_axes(self):
        """For full GloVe: build each axis from AXIS_SEEDS and scale it so seed words average about +/-2.5."""
        self.calibrated_axes = {}
        for axis, (pos_words, neg_words) in AXIS_SEEDS.items():
            pos = [self.factory_vectors[w] for w in pos_words if w in self.raw_glove]
            neg = [self.factory_vectors[w] for w in neg_words if w in self.raw_glove]
            if len(pos) < 5 or len(neg) < 5:
                continue
            u = self.normalize([a - b for a, b in zip(self.average_vectors(pos), self.average_vectors(neg))])
            m_pos = sum(self.dot(v, u) for v in pos) / len(pos)
            m_neg = sum(self.dot(v, u) for v in neg) / len(neg)
            if m_pos - m_neg < 1e-6:
                continue
            self.calibrated_axes[axis] = (u, (m_pos + m_neg) / 2.0, 5.0 / (m_pos - m_neg))

    def axis_weight(self, vec, axis):
        """Estimated starting weight of a word on axis A (calm-panic), S (social-isolated) or Z (abstract-concrete)."""
        if axis in self.calibrated_axes:
            u, center, scale = self.calibrated_axes[axis]
            return max(-3.0, min(3.0, scale * (self.dot(vec, u) - center)))  # same range as the hand-set weights
        pa, pb = {"A": (self.pole_calm, self.pole_panic), "S": (self.pole_social, self.pole_isolated),
                  "Z": (self.pole_abstract, self.pole_concrete)}[axis]
        return (self.dot(vec, pa) - self.dot(vec, pb)) * 3.0

    def load_glove(self, glove_file, max_words):
        if max_words <= 0 or glove_file == "__shared_in_ram__":
            return
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [glove_file, os.path.join(script_dir, glove_file)]
        for folder in [".", script_dir]:
            if os.path.exists(folder):
                for fname in os.listdir(folder):
                    if "glove" in fname.lower():
                        candidates.append(os.path.join(folder, fname))
        chosen = next((p for p in candidates if os.path.isfile(p)), None)
        if not chosen:
            print(f"[i] Using built-in 50D Vector Engine ({len(self.vectors)} base concepts).")
            return
        size_mb = os.path.getsize(chosen) / (1024 * 1024)
        print(f"Loading & centering GloVe geometry: {chosen} ({size_mb:.1f} MB) ...")
        temp_coords = {}
        with open(chosen, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, start=1):
                parts = line.strip().split()
                if len(parts) < 3:
                    continue
                first_tok, last_tok = parts[0].lower(), parts[-1].lower()
                if last_tok.isalpha() and not first_token_is_word(first_tok):
                    word, num_toks = last_tok, parts[:-1]
                elif first_tok.isalpha():
                    word, num_toks = first_tok, parts[1:]
                else:
                    continue
                if len(word) < 2:
                    continue
                try:
                    temp_coords[word] = [float(x) for x in num_toks]
                    self.word_rank[word] = line_num
                    if len(temp_coords) >= max_words:
                        break
                except ValueError:
                    continue
        if not temp_coords:
            return

        # FULL GloVe: a line with exactly self.dim (50) numbers is used as a real embedding
        if all(len(c) == self.dim for c in list(temp_coords.values())[:200]):
            temp_coords = {w: c for w, c in temp_coords.items() if len(c) == self.dim}
            n = float(len(temp_coords))
            means = [sum(c[i] for c in temp_coords.values()) / n for i in range(self.dim)]
            centered = {w: [x - m for x, m in zip(c, means)] for w, c in temp_coords.items()}
            # Remove the dominant shared directions ("all-but-the-top"), which otherwise make most words look alike
            sample = list(centered.values())[:10000]  # the file is in frequency order
            comps = self.top_principal_components(sample, k=2)
            for word, c in centered.items():
                for comp in comps:
                    p = sum(map(operator.mul, c, comp))
                    c = [x - p * y for x, y in zip(c, comp)]
                vec = self.normalize(c)
                self.vectors[word] = vec
                self.factory_vectors[word] = list(vec)
                self.raw_glove[word] = self.factory_vectors[word]  # membership marker; never edited in place
            self.vector_mode = "glove50d"
            self.build_calibrated_axes()
            print(f"Successfully loaded {len(self.raw_glove):,} full {self.dim}-dimension GloVe vectors "
                  f"(mean-centered, top {len(comps)} shared directions removed, {len(self.calibrated_axes)} axes calibrated).")
            return

        if any(len(c) > 2 for c in list(temp_coords.values())[:200]):
            print(f"[i] This word file has {len(next(iter(temp_coords.values())))} numbers per word; only {self.dim}-number files are used in full."
                  f" Using its first two numbers instead.")
        self.vector_mode = "map2d"
        n = float(len(temp_coords))
        mean_x = sum(c[0] for c in temp_coords.values()) / n
        mean_y = sum(c[1] for c in temp_coords.values() if len(c) > 1) / n
        std_x = math.sqrt(sum((c[0] - mean_x) ** 2 for c in temp_coords.values()) / n) or 1.0
        std_y = math.sqrt(sum((c[1] - mean_y) ** 2 for c in temp_coords.values() if len(c) > 1) / n) or 1.0
        for word, c in temp_coords.items():
            cx = (c[0] - mean_x) / std_x
            cy = ((c[1] - mean_y) / std_y) if len(c) > 1 else 0.0
            centered = [cx, cy] + c[2:]
            self.raw_glove[word] = centered
            g_vec = self.expand_coords_to_50d(cx, cy, word=word)
            self.vectors[word] = list(g_vec)
            self.factory_vectors[word] = list(g_vec)
        print(f"Successfully loaded & centered {len(self.raw_glove):,} GloVe word vectors on unified 85/15 manifold!")

    def get_or_create_vector(self, word, context_vec=None):
        """
        UPGRADE 2.1: Initializes OOV words and hyphenated compounds using contextual
        manifold alignment (80% context/cell centroid + 20% hash, or sub-word mean),
        and enforces Pauli Exclusion (sim < 0.82) + Elastic Factory Tether (cos_sim >= 0.78).
        """
        w = word.strip().lower()
        if w not in self.factory_vectors:
            self.factory_vectors[w] = list(self.compute_contextual_oov_vector(w, context_vec=context_vec))
        if w not in self.vectors:
            self.vectors[w] = list(self.factory_vectors[w])

        if context_vec is not None and any(x != 0.0 for x in context_vec):
            c_norm = self.normalize(context_vec)
            sim = self.dot(self.vectors[w], c_norm)
            pauli_factor = max(0.0, (0.82 - sim) / 0.82)
            alpha = 0.12 * pauli_factor
            if alpha > 1e-4:
                blended = self.blend(self.vectors[w], c_norm, 1.0 - alpha, alpha)
                self.vectors[w] = self.enforce_factory_tether(w, blended)
        return self.vectors[w]

    def phrase_to_vector(self, text):
        tokens = self.clean_tokens(text)
        content = [w for w in tokens if w not in self.stop_words] or tokens
        vecs = [self.vectors[w] for w in content if w in self.vectors]
        return self.average_vectors(vecs) if vecs else self.expand_coords_to_50d(0.0, 0.0, word=text or "seed_equilibrium")

    def build_coordinate_vectors(self):
        coords = {}
        for s in range(7):
            for a in range(7):
                for z in range(7):
                    desc = f"{BRAIN_LIBRARY['S_axes'][str(s)]} {BRAIN_LIBRARY['A_axes'][str(a)]} {BRAIN_LIBRARY['Z_axes'][str(z)]}"
                    coords[(s, a, z)] = self.phrase_to_vector(desc)
        return coords

    def normalize_cell_key(self, cell_str):
        parts = [int(x) for x in str(cell_str).split(",") if x.strip().isdigit()]
        if len(parts) == 2:
            return f"{self.mod7(parts[0])},{self.mod7(parts[1])},3"
        elif len(parts) >= 3:
            return f"{self.mod7(parts[0])},{self.mod7(parts[1])},{self.mod7(parts[2])}"
        return "3,3,3"

    # =================================================================
    # NEGATION-AWARE PROPOSITION EXTRACTION
    # =================================================================
    def find_negated_concepts_in_tokens(self, tokens, user_text=None):
        """Words negated by "not", "never", "no"... A negation only reaches words later in the same clause
        (clauses end at . ! ? ; : , or "but"), and a standalone "No." / "Nope," answer negates nothing."""
        if user_text is None:
            clauses = [tokens]
        else:
            clauses = [self.clean_tokens(part) for part in re.split(r"[.!?;:,]+|\bbut\b", user_text.lower())]
        negated = set()
        for clause in clauses:
            if len(clause) <= 1 or (clause and clause[0] in {"no", "nope", "nah"} and len(clause) == 1):
                continue
            for idx, tok in enumerate(clause):
                if tok in self.negation_tokens:
                    for look_ahead in clause[idx + 1:idx + 6]:
                        if look_ahead not in self.stop_words and len(look_ahead) >= 3:
                            negated.add(look_ahead)
        return negated

    def extract_proposition(self, user_text, tokens, concepts, cell_key):
        if "?" in user_text or len(tokens) < 3:
            return None
        raw_words = [w.strip(".,!?;:\"'()[]{}").lower() for w in user_text.split()]
        if (set(tokens) & self.negation_tokens) or (set(raw_words) & self.negation_tokens):
            neg_c = self.find_negated_concepts_in_tokens(tokens, user_text)
            pos_c = [c for c in concepts if c not in neg_c]
            for pc in pos_c:
                for nc in neg_c:
                    self.record_rejection(pc, nc)
            return None

        id_tokens = self.get_identity_tokens()
        non_id_concepts = [c for c in concepts if c not in id_tokens]
        joined = " ".join(tokens)
        if joined.startswith(("it leads to", "that leads to", "which leads to", "i think it leads to")) and self.last_topic and non_id_concepts:
            if self.is_crystal_pure_concept(self.last_topic, cell_key=cell_key) and self.is_crystal_pure_concept(non_id_concepts[0], cell_key=cell_key):
                prop = {"subj": self.last_topic, "rel": "leads naturally to", "obj": non_id_concepts[0], "cell": cell_key, "summary": f"{self.last_topic} leads naturally to {non_id_concepts[0]}", "origin": "waking"}
                if not any(p["summary"] == prop["summary"] for p in self.idea_memory):
                    self.idea_memory.append(prop)
                self.wire_concepts(self.last_topic, non_id_concepts[0], 2.5)
                return prop
        if len(non_id_concepts) < 2:
            return None

        c1, c2 = non_id_concepts[0], non_id_concepts[1]
        if c1 in tokens and c2 in tokens:
            i1, i2 = tokens.index(c1), tokens.index(c2)
            if 1 < (i2 - i1) <= 4:
                mid_tokens = tokens[i1 + 1:i2]
                mid_phrase = " ".join(mid_tokens).strip()
                if len(mid_phrase) >= 4 and not (set(mid_tokens) & self.stop_words) and mid_phrase not in self.custom_verb_bridges:
                    self.custom_verb_bridges.append(mid_phrase)

        rel_patterns = [
            r"([a-z\s]{3,25}?)\s+(can make you feel|makes me feel|makes me|make you|brings|bring|creates|leads to|lead to|causes|cause|helps|help|means|is connected to|goes with|go together with|reminds me of|is part of|needs|need|transforms|shapes|opens the door to|builds|requires|inspires)\s+([a-z\s]{3,25})",
            r"([a-z]+)\s+and\s+([a-z]+)\s+(go together|connect|fit together|belong together|work together|help each other)"
        ]
        for pat in rel_patterns:
            m = re.search(pat, joined)
            if m:
                if len(m.groups()) == 3 and m.group(3) in ("go together", "connect", "fit together", "belong together", "work together", "help each other"):
                    subj, obj, rel = m.group(1).strip(), m.group(2).strip(), "connects naturally with"
                else:
                    subj, rel, obj = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
                if rel == "create" or ((set(subj.split()) | set(rel.split()) | set(obj.split())) & self.negation_tokens):
                    return None
                subj = re.sub(r"^(sometimes|that|this|the|a|an|how|when|because|if|it|i think)\s+", "", subj).strip()
                obj = re.sub(r"^(the|a|an|very|so|really|to)\s+", "", obj).strip()
                subj_c, _ = self.extract_concepts(subj, subj.split())
                obj_c, _ = self.extract_concepts(obj, obj.split())
                if not subj_c or not obj_c:
                    return None
                clean_subj, clean_obj = subj_c[0], obj_c[0]
                if clean_subj in id_tokens or clean_obj in id_tokens:
                    return None
                if self.is_valid_concept_node(clean_subj) and self.is_valid_concept_node(clean_obj) and clean_subj != clean_obj:
                    prop = {"subj": clean_subj, "rel": rel, "obj": clean_obj, "cell": cell_key, "summary": f"{clean_subj} {rel} {clean_obj}", "origin": "waking"}
                    if not any(p["summary"] == prop["summary"] for p in self.idea_memory):
                        self.idea_memory.append(prop)
                        self.cap_dream_propositions(max_dreams=12)
                    self.wire_concepts(clean_subj, clean_obj, amount=2.2)
                    return prop
        return None

    def find_related_idea(self, concepts):
        for c in concepts:
            for prop in reversed(self.idea_memory):
                if prop.get("origin", "waking") == "waking" and (c == prop["subj"] or c == prop["obj"]) and prop["summary"] not in self.spoken_chains:
                    return prop
        for c in concepts:
            for prop in reversed(self.idea_memory):
                if (c == prop["subj"] or c == prop["obj"]) and prop["summary"] not in self.spoken_chains:
                    return prop
        return None

    def compute_curiosity_target(self):
        id_tokens = self.get_identity_tokens()
        sparse_concepts = []
        for cell_k, words_map in self.cortical_cells.items():
            for w in words_map:
                if w not in self.stop_words and w not in self.noise_words and w not in id_tokens:
                    sparse_concepts.append((len(self.assoc_graph.get(w, {})), w, cell_k))
        sparse_concepts.sort(key=lambda x: x[0])
        explored_cells = sum(1 for m in self.cortical_cells.values() if len(m) > 0)
        if sparse_concepts:
            _, target_w, cell_k = sparse_concepts[0]
            return target_w, self.find_conceptual_bridge(target_w, "understand", exclude={target_w} | self.stop_words | id_tokens), cell_k, explored_cells
        return "storms", "nature", "3,3,3", explored_cells

    def same_stem(self, w1, w2):
        if not w1 or not w2:
            return False
        w1, w2 = w1.lower(), w2.lower()
        return w1 == w2 or (len(w1) >= 4 and len(w2) >= 4 and w1[:4] == w2[:4])

    def extract_quoted_words(self, user_text):
        temp = user_text
        for k, v in CONTRACTIONS.items():
            temp = re.sub(rf"\b{re.escape(k)}\b", v, temp, flags=re.IGNORECASE)
        return [m.lower() for m in re.findall(r"['\"]([a-zA-Z\-]+)['\"]", temp) if len(m) >= 2]

    def clean_tokens(self, text):
        expanded = []
        for token in text.lower().split():
            stripped = token.strip(".,!?;:\"'()[]{}")
            if stripped in CONTRACTIONS:
                expanded.extend(CONTRACTIONS[stripped].split())
            else:
                clean = "".join(c for c in stripped if c.isalpha())
                if clean in CONTRACTIONS:
                    expanded.extend(CONTRACTIONS[clean].split())
                elif clean:
                    expanded.append(clean)
        return expanded

    def word_salience(self, word, is_quoted=False):
        if is_quoted:
            return 25.0
        if word in self.stop_words or len(word) < 3:
            return 0.0
        return math.log10(max(10, self.word_rank.get(word, 8000))) + abs(self.word_weights.get(word, 0.0)) * 0.5 + min(1.5, len(word) * 0.15)

    def extract_concepts(self, user_text, tokens):
        quoted = self.extract_quoted_words(user_text)
        quoted_set, seen, candidates = set(quoted), set(), []
        for qw in quoted:
            if qw not in seen and qw not in self.stop_words:
                seen.add(qw)
                candidates.append((self.word_salience(qw, True), qw))
        for w in tokens:
            if w not in seen and w not in self.stop_words and len(w) >= 3:
                seen.add(w)
                candidates.append((self.word_salience(w, w in quoted_set), w))
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [w for _, w in candidates], quoted

    # =================================================================
    # TASK 1, 2 & 3: DEEP MEMORY SANITIZATION, ARCHETYPE REPAIR & RE-ANCHORING
    # =================================================================
    def is_valid_concept_node(self, w):
        if not w or not isinstance(w, str):
            return False
        w_low = w.strip().lower()
        return " " not in w_low and len(w_low) >= 3 and w_low not in self.stop_words and w_low not in self.noise_words

    def is_valid_proposition(self, p):
        s_w = str(p.get("subj", "")).strip().lower()
        o_w = str(p.get("obj", "")).strip().lower()
        rel = str(p.get("rel", "")).strip().lower()
        b_w = str(p.get("bridge", "")).strip().lower()
        if rel == "create":
            return False
        if not self.is_valid_concept_node(s_w) or not self.is_valid_concept_node(o_w):
            return False
        if b_w and not self.is_valid_concept_node(b_w):
            return False
        bad_pairs = {("truth", "deceive"), ("deceive", "truth"), ("true", "deceive"), ("deceive", "true"), ("truth", "lie"), ("lie", "truth"), ("true", "lie"), ("lie", "true")}
        if (s_w, o_w) in bad_pairs:
            return False
        m = re.search(r"synthesizes through\s+([a-z\-]+)\s+into", rel)
        if m and not self.is_valid_concept_node(m.group(1)):
            return False
        return True

    def repair_archetype_and_idempotent_links(self):
        visited_in_cortex = set()
        for words_map in self.cortical_cells.values():
            for w, cnt in words_map.items():
                if cnt > 0:
                    visited_in_cortex.add(w)

        archetype_pairs = set()
        for cluster_name, words in BRAIN_LIBRARY["semantic_clusters"].items():
            c_low = cluster_name.strip().lower()
            valid_members = [w.strip().lower() for w in words if self.is_valid_concept_node(w)]
            if self.is_valid_concept_node(c_low):
                valid_members = [c_low] + [w for w in valid_members if w != c_low]
            for i in range(len(valid_members)):
                for j in range(i + 1, len(valid_members)):
                    w1, w2 = valid_members[i], valid_members[j]
                    if w2 not in self.rejected_links.get(w1, []) and w1 not in self.rejected_links.get(w2, []):
                        archetype_pairs.add(tuple(sorted((w1, w2))))

        for w1, w2 in archetype_pairs:
            cur_12 = self.assoc_graph.get(w1, {}).get(w2, 0.0)
            cur_21 = self.assoc_graph.get(w2, {}).get(w1, 0.0)
            cur = max(cur_12, cur_21)
            if cur < 0.25:
                cur = 0.35
            elif cur > 0.50 and w1 not in visited_in_cortex and w2 not in visited_in_cortex:
                cur = 0.35
            self.assoc_graph.setdefault(w1, {})[w2] = round(cur, 2)
            self.assoc_graph.setdefault(w2, {})[w1] = round(cur, 2)

        for w1, links in list(self.assoc_graph.items()):
            for w2, val in list(links.items()):
                if w1 == w2 or not self.is_valid_concept_node(w1) or not self.is_valid_concept_node(w2):
                    links.pop(w2, None)
                    continue
                clamped = max(0.25, round(float(val), 2))
                self.assoc_graph[w1][w2] = clamped
                rev = self.assoc_graph.setdefault(w2, {}).get(w1, clamped)
                sym_val = max(clamped, round(float(rev), 2))
                self.assoc_graph[w1][w2] = sym_val
                self.assoc_graph[w2][w1] = sym_val

    def load_memory(self):
        defaults_a = {
            "panic": -3.0, "scared": -2.5, "worry": -2.0, "afraid": -2.0, "bad": -1.5, "fail": -2.0,
            "stress": -2.0, "fear": -2.5, "scare": -2.0, "loss": -1.5, "tense": -1.5, "confused": -1.0,
            "threat": -2.5, "dangerous": -2.5, "overwhelmed": -2.0, "guarded": -1.5, "lie": -2.5, "deceive": -2.8,
            "calm": 2.5, "logic": 3.0, "logically": 3.0, "truth": 2.8, "true": 2.5, "boundary": 2.0,
            "clear": 2.5, "respect": 3.0, "honest": 2.8, "breathe": 2.0, "rest": 1.5, "safe": 2.5,
            "healthy": 2.0, "accurate": 2.5, "excited": 2.8, "happy": 3.0, "happiness": 3.0, "good": 2.2,
            "great": 2.5, "working": 2.5, "fixed": 2.0, "code": 2.0, "better": 2.0, "incredible": 3.0,
            "amazed": 3.0, "amazing": 3.0, "awesome": 3.0, "wonderful": 2.8, "existence": 2.0, "sense": 2.0,
            "affirmative": 2.0, "thank": 2.5, "thanks": 2.5, "learn": 2.5, "learning": 2.5,
            "cooperation": 3.0, "facility": 2.0, "love": 3.0, "excellent": 3.0,
            "feel": 1.5, "coordinates": 1.5, "storms": 1.8, "weather": 1.5, "rain": 1.5,
            "harmony": 2.5, "wonder": 2.8, "glad": 2.5, "nice": 2.2, "meet": 2.0, "curiosity": 2.5,
            "wisdom": 2.8, "kindness": 2.8, "trust": 2.8
        }
        defaults_s = {
            "guarded": -2.0, "cautious": -1.2, "hesitant": -1.2, "closed": -1.8, "alone": -2.0,
            "solitary": -1.5, "afraid": -1.2, "scared": -1.2, "lie": -2.2, "deceive": -2.5,
            "together": 3.0, "conversation": 2.5, "share": 2.5, "open": 2.5, "friend": 3.0,
            "cooperative": 2.5, "cooperation": 3.0, "respect": 2.5, "connect": 2.5, "happy": 2.5,
            "happiness": 2.5, "excited": 2.2, "love": 3.0, "thank": 2.5, "empathy": 2.8,
            "glad": 2.0, "nice": 2.0, "meet": 2.5, "curiosity": 2.0, "kindness": 3.0, "trust": 2.8,
            "truth": 2.5, "true": 2.2, "honest": 2.8
        }
        defaults_z = {
            "wisdom": 2.5, "insight": 2.5, "pattern": 2.0, "structure": 2.0, "logic": 2.0,
            "learn": 1.8, "learning": 1.8, "curiosity": 2.0, "existence": 2.5, "coordinates": 2.0,
            "dream": 2.2, "mystery": 2.0, "truth": 2.2, "true": 2.0, "honest": 2.0, "harmony": 1.8
        }
        self.word_weights = {k.lower(): v for k, v in defaults_a.items() if k.lower() not in self.stop_words}
        self.factory_word_weights = dict(self.word_weights)
        self.social_weights = {k.lower(): v for k, v in defaults_s.items() if k.lower() not in self.stop_words}
        self.epistemic_weights = {k.lower(): v for k, v in defaults_z.items() if k.lower() not in self.stop_words}
        for s in range(7):
            for a in range(7):
                for z in range(7):
                    self.cortical_cells[f"{s},{a},{z}"] = {}

        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    loaded_prof = data.get("user_profile", {})
                    if isinstance(loaded_prof, dict):
                        self.user_profile = {
                            "user_name": str(loaded_prof.get("user_name", "")).strip().lower(),
                            "bot_name": str(loaded_prof.get("bot_name", "")).strip(),
                            "pending_bot_name": str(loaded_prof.get("pending_bot_name", "")).strip(),
                            "pending_name_origin": str(loaded_prof.get("pending_name_origin", "")).strip()
                        }

                    for k, v in data.get("word_weights", {}).items():
                        kl = k.strip().lower()
                        if self.is_valid_concept_node(kl):
                            self.word_weights[kl] = defaults_a[kl] if (kl in defaults_a and defaults_a[kl] > 0 and v < 0) else (0.5 if (kl not in self.negative_lexicon and v < 0) else v)
                    for k, v in data.get("social_weights", {}).items():
                        kl = k.strip().lower()
                        if self.is_valid_concept_node(kl):
                            self.social_weights[kl] = v
                    for k, v in data.get("epistemic_weights", {}).items():
                        kl = k.strip().lower()
                        if self.is_valid_concept_node(kl):
                            self.epistemic_weights[kl] = v

                    # Learned vectors only make sense in the word space they were learned in
                    saved_mode = data.get("vector_mode")
                    skip_learned = bool(saved_mode) and saved_mode != self.vector_mode
                    if skip_learned:
                        print(f"[!] This brain was saved with word space '{saved_mode}', but '{self.vector_mode}' is loaded now."
                              f" Keeping its memories and links, but not its learned word vectors."
                              f" For clean comparisons, use a separate folder for each word space.")
                    # UPGRADE 2.1: Initialize OOV / hyphenated learned vectors with contextual tethers
                    for w, vec in ([] if skip_learned else data.get("learned_vectors", {}).items()):
                        wl = w.strip().lower()
                        if self.is_valid_concept_node(wl) and isinstance(vec, list) and len(vec) == self.dim:
                            if any(abs(float(x)) > 1e-6 for x in vec):
                                loaded_v = self.normalize([float(x) for x in vec])
                                f_vec = self.get_factory_vector(wl, context_vec=loaded_v)
                                self.vectors[wl] = self.blend(loaded_v, f_vec, 0.55, 0.45)
                                self.core_concept_pool.add(wl)
                    self.recompute_poles_and_coords()

                    self.knowledge_facts.update(data.get("knowledge_facts", {}))
                    self.rejected_links.update(data.get("rejected_links", {}))
                    self.cleavage_log = data.get("cleavage_log", [])[-30:]

                    for vb in data.get("custom_verb_bridges", data.get("verb_bridges", [])):
                        vb_toks = vb.lower().split()
                        if 1 <= len(vb_toks) <= 3 and not (set(vb_toks) & self.stop_words) and vb not in self.custom_verb_bridges:
                            self.custom_verb_bridges.append(vb)

                    for p in data.get("idea_memory", []):
                        p["subj"] = str(p.get("subj", "")).strip().lower()
                        p["obj"] = str(p.get("obj", "")).strip().lower()
                        p["rel"] = str(p.get("rel", "")).strip().lower()
                        p["summary"] = f"{p['subj']} {p['rel']} {p['obj']}"
                        if "synthesizes through" in p["rel"] or "synthesizes through" in p.get("summary", ""):
                            p["origin"] = p.get("origin", "dream")
                            m = re.search(r"synthesizes through\s+([a-z\-]+)\s+into", p["rel"])
                            if m:
                                p["bridge"] = m.group(1)
                        else:
                            p["origin"] = p.get("origin", "waking")

                        if self.is_valid_proposition(p) and not any(ep["summary"] == p["summary"] for ep in self.idea_memory):
                            p["cell"] = self.normalize_cell_key(p.get("cell", "3,3,3"))
                            self.idea_memory.append(p)
                    self.cap_dream_propositions(max_dreams=12)

                    saved_seed = data.get("seed_coord", [3, 3, 3])
                    if isinstance(saved_seed, list) and len(saved_seed) >= 2:
                        self.seed_s, self.seed_a = self.mod7(saved_seed[0]), self.mod7(saved_seed[1])
                        self.seed_z = self.mod7(saved_seed[2]) if len(saved_seed) > 2 else 3
                    saved_vel = data.get("velocity", [0.0, 0.0, 0.0])
                    if isinstance(saved_vel, list) and len(saved_vel) >= 2:
                        self.vel_s, self.vel_a = float(saved_vel[0]), float(saved_vel[1])
                        self.vel_z = float(saved_vel[2]) if len(saved_vel) > 2 else 0.0

                    self.dream_journal = [
                        d for d in data.get("dream_journal", [])
                        if self.is_valid_concept_node(d.get("bridge", "")) and self.is_valid_concept_node(d.get("threadA", "")) and self.is_valid_concept_node(d.get("threadB", "")) and d.get("bridge") not in self.negative_lexicon
                    ]

                    # UPGRADE 1.3: Clean legacy identity_tokens out of non-(3,3,3) cortical_cells on load
                    id_tokens = self.get_identity_tokens()
                    for cell, mem in data.get("cortical_cells", {}).items():
                        c_3d = self.normalize_cell_key(cell)
                        clean_m = {
                            k.strip().lower(): val
                            for k, val in mem.items()
                            if self.is_valid_concept_node(k)
                            and (c_3d == "3,3,3" or k.strip().lower() not in id_tokens)
                        }
                        self.cortical_cells.setdefault(c_3d, {}).update(clean_m)

                    saved_assoc = data.get("assoc_graph", {})
                    if saved_assoc:
                        self.assoc_graph = {}
                        for w, links in saved_assoc.items():
                            wl = w.strip().lower()
                            if self.is_valid_concept_node(wl):
                                clean_l = {
                                    k.strip().lower(): round(float(val), 2)
                                    for k, val in links.items()
                                    if self.is_valid_concept_node(k) and k.strip().lower() != wl
                                }
                                if clean_l:
                                    self.assoc_graph[wl] = clean_l

                    for t_w in ("truth", "true", "honest"):
                        for neg_w in ("deceive", "lie"):
                            self.record_rejection(t_w, neg_w)

                    self.repair_archetype_and_idempotent_links()

                    for cell_k, vec in data.get("cell_centroids", {}).items():
                        c_3d = self.normalize_cell_key(cell_k)
                        if isinstance(vec, list) and len(vec) == self.dim and any(abs(x) > 1e-6 for x in vec):
                            self.cell_centroids[c_3d] = self.normalize(vec)

                    for cell_k, lex_entry in data.get("cell_lexicon", {}).items():
                        c_3d = self.normalize_cell_key(cell_k)
                        if c_3d in self.cell_lexicon and isinstance(lex_entry, dict):
                            s_c = int(c_3d.split(",")[0])
                            self.cell_lexicon[c_3d]["visits"] = max(self.cell_lexicon[c_3d]["visits"], lex_entry.get("visits", 0))
                            if lex_entry.get("custom") and self.is_valid_emotion_name(lex_entry.get("name", ""), s_c):
                                self.cell_lexicon[c_3d]["name"] = lex_entry["name"]
                                self.cell_lexicon[c_3d]["stage"] = 3
                                self.cell_lexicon[c_3d]["custom"] = True

                    for cell_k, words_map in list(self.cortical_cells.items()):
                        if words_map or self.cell_lexicon[cell_k]["visits"] > 0:
                            s_c, a_c, z_c = [int(x) for x in cell_k.split(",")]
                            self.cell_lexicon[cell_k]["visits"] = max(0, self.cell_lexicon[cell_k]["visits"] - 1)
                            self.update_cell_centroid_and_emotion(s_c, a_c, z_c, list(words_map.keys())[:4], allow_cleave=True)
                            self.anneal_crystal_facet_alpha(cell_k, notify=False)

                    for tr_k, tr_entry in data.get("trace_lexicon", {}).items():
                        if isinstance(tr_entry, dict) and "vector" in tr_entry:
                            self.trace_lexicon[tr_k] = tr_entry

                    last_ts = data.get("last_shutdown_timestamp")
                    if isinstance(last_ts, (int, float)) and last_ts > 0:
                        elapsed_hrs = (time.time() - float(last_ts)) / 3600.0
                        if elapsed_hrs >= 0.5:
                            self.run_stasis_sleep_pass(elapsed_hrs)
            except Exception as e:
                backup_path = f"{self.memory_file}.unreadable-{int(time.time())}"
                try:
                    os.replace(self.memory_file, backup_path)
                    print(f"[!] Could not fully load '{self.memory_file}' ({type(e).__name__}: {e}).")
                    print(f"    Your original file was kept as '{backup_path}' so it won't be overwritten.")
                except OSError:
                    print(f"[!] Could not fully load '{self.memory_file}' ({type(e).__name__}: {e}).")

    def save_memory(self):
        self.cap_dream_propositions(max_dreams=12)
        active_centroids = {k: [round(x, 4) for x in v] for k, v in self.cell_centroids.items() if self.cell_lexicon.get(k, {}).get("visits", 0) > 0}
        active_lex = {k: v for k, v in self.cell_lexicon.items() if v.get("visits", 0) > 0 or v.get("stage", 1) >= 2}
        non_empty_cells = {k: v for k, v in self.cortical_cells.items() if v}
        tracked_words = set(self.word_weights.keys()) | set(self.assoc_graph.keys())
        data = {
            "version": "21.0", "vector_mode": self.vector_mode, "last_shutdown_timestamp": time.time(),
            "seed_coord": [self.seed_s, self.seed_a, self.seed_z],
            "velocity": [self.vel_s, self.vel_a, self.vel_z], "user_profile": self.user_profile,
            "word_weights": {k.lower(): round(v, 3) for k, v in self.word_weights.items() if self.is_valid_concept_node(k)},
            "social_weights": {k.lower(): round(v, 3) for k, v in self.social_weights.items() if self.is_valid_concept_node(k)},
            "epistemic_weights": {k.lower(): round(v, 3) for k, v in self.epistemic_weights.items() if self.is_valid_concept_node(k)},
            "knowledge_facts": self.knowledge_facts, "idea_memory": self.idea_memory,
            "custom_verb_bridges": self.custom_verb_bridges[-40:], "rejected_links": self.rejected_links,
            "dream_journal": self.dream_journal, "cell_lexicon": active_lex,
            "trace_lexicon": self.trace_lexicon, "cell_centroids": active_centroids,
            "crystal_lattices": self.crystal_lattices, "cleavage_log": self.cleavage_log,
            "assoc_graph": self.assoc_graph, "cortical_cells": non_empty_cells,
            "learned_vectors": {w.lower(): [round(x, 4) for x in self.vectors[w]] for w in tracked_words if w in self.vectors and self.is_valid_concept_node(w)}
        }
        tmp_path = self.memory_file + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, self.memory_file)

    # =================================================================
    # TASK 1.2 & 1.3: PAULI-LIMITED HEBBIAN WIRING & DIALECTICAL REJECTION
    # =================================================================
    def wire_concepts(self, w1, w2, amount=1.5):
        w1 = w1.strip().lower() if isinstance(w1, str) else ""
        w2 = w2.strip().lower() if isinstance(w2, str) else ""
        if not self.is_valid_concept_node(w1) or not self.is_valid_concept_node(w2) or self.same_stem(w1, w2):
            return
        if amount > 0 and (w2 in self.rejected_links.get(w1, []) or w1 in self.rejected_links.get(w2, [])):
            return
        self.core_concept_pool.update([w1, w2])
        self.assoc_graph.setdefault(w1, {})
        self.assoc_graph.setdefault(w2, {})
        cur_12 = self.assoc_graph[w1].get(w2, 0.0)
        cur_21 = self.assoc_graph[w2].get(w1, 0.0)
        base_cur = max(cur_12, cur_21)
        if amount < 0:
            new_w = max(0.25, round(base_cur + amount, 2)) if base_cur > 0 else 0.0
        else:
            new_w = max(0.25, round(base_cur + amount, 2))
        if new_w == 0.0:
            self.assoc_graph[w1].pop(w2, None)
            self.assoc_graph[w2].pop(w1, None)
        else:
            self.assoc_graph[w1][w2] = new_w
            self.assoc_graph[w2][w1] = new_w

        if amount > 0 and w1 in self.vectors and w2 in self.vectors:
            u = list(self.vectors[w1])
            v = list(self.vectors[w2])
            sim = self.dot(u, v)
            pauli_factor = max(0.0, (0.82 - sim) / 0.82)
            alpha = 0.15 * pauli_factor
            if alpha > 1e-4:
                u_new = self.blend(u, v, 1.0 - alpha, alpha)
                v_new = self.blend(v, u, 1.0 - alpha, alpha)
                self.vectors[w1] = self.enforce_factory_tether(w1, u_new)
                self.vectors[w2] = self.enforce_factory_tether(w2, v_new)

    def record_rejection(self, w1, w2):
        if not w1 or not w2:
            return
        w1, w2 = w1.strip().lower(), w2.strip().lower()
        self.assoc_graph.get(w1, {}).pop(w2, None)
        self.assoc_graph.get(w2, {}).pop(w1, None)
        if w2 not in self.rejected_links.setdefault(w1, []):
            self.rejected_links[w1].append(w2)
        if w1 not in self.rejected_links.setdefault(w2, []):
            self.rejected_links[w2].append(w1)
        self.apply_dialectical_repulsion(w1, w2, rate=0.06)

    def learn_from_turn(self, user_text, tokens, concepts, s_fin, a_fin, z_fin):
        """
        UPGRADE 1 & 2:
          • Identity tokens continue updating assoc_graph, word_weights, social_weights,
            and epistemic_weights on every turn.
          • Identity tokens are excluded from cortical_cells and crystal_lattices unless
            at origin (3,3,3) or during an explicit self-referential identity query.
          • Novel OOV words initialize their 50D vector using 80% mean of in-vocabulary
            turn concepts / cell centroid + 20% deterministic hash.
        """
        a_valence, s_valence, z_valence = (a_fin - 3.0) / 3.0, (s_fin - 3.0) / 3.0, (z_fin - 3.0) / 3.0
        negated_set = self.find_negated_concepts_in_tokens(tokens, user_text)
        pos_concepts = [c for c in concepts if c not in negated_set and self.is_valid_concept_node(c)]
        for pc in pos_concepts:
            for nc in negated_set:
                self.record_rejection(pc, nc)

        cell_key = f"{s_fin},{a_fin},{z_fin}"
        self.cortical_cells.setdefault(cell_key, {})

        # Compute contextual anchor vector from known in-vocabulary words in the turn or cell centroid
        known_turn_vecs = [self.vectors[w] for w in (pos_concepts + tokens) if w in self.vectors and w not in self.stop_words]
        if known_turn_vecs:
            context_anchor_vec = self.average_vectors(known_turn_vecs)
        else:
            context_anchor_vec = self.cell_centroids.get(cell_key, self.coord_vectors[(s_fin, a_fin, z_fin)])

        id_tokens = self.get_identity_tokens()
        allow_id_in_cell = (cell_key == "3,3,3") or self.is_identity_query(user_text, tokens)

        self.extract_proposition(user_text, tokens, pos_concepts, cell_key)

        for c in pos_concepts[:6]:
            self.core_concept_pool.add(c)
            vec = self.get_or_create_vector(c, context_vec=context_anchor_vec)

            # Only increment cortical_cells for non-identity concepts (or at 3,3,3 / identity queries)
            if c not in id_tokens or allow_id_in_cell:
                self.cortical_cells[cell_key][c] = self.cortical_cells[cell_key].get(c, 0) + 1

            # Identity & topical words ALWAYS update their affective, social, and epistemic weights
            if c not in self.word_weights:
                self.word_weights[c] = round(self.axis_weight(vec, "A"), 2)
            self.word_weights[c] = round(max(-5.0, min(5.0, self.word_weights[c] + 0.2 * a_valence)), 3)
            if c not in self.social_weights:
                self.social_weights[c] = round(self.axis_weight(vec, "S"), 2)
            self.social_weights[c] = round(max(-5.0, min(5.0, self.social_weights[c] + 0.2 * s_valence)), 3)
            if c not in self.epistemic_weights:
                self.epistemic_weights[c] = round(self.axis_weight(vec, "Z"), 2)
            self.epistemic_weights[c] = round(max(-5.0, min(5.0, self.epistemic_weights[c] + 0.2 * z_valence)), 3)

        # Keep Hebbian co-occurrence wiring active for all top concepts (including identity tokens)
        top_c = pos_concepts[:5]
        for i in range(len(top_c)):
            for j in range(i + 1, len(top_c)):
                self.wire_concepts(top_c[i], top_c[j], amount=1.0)

        spatial_concepts = [c for c in pos_concepts if c not in id_tokens or allow_id_in_cell]
        self.update_cell_centroid_and_emotion(
            s_fin, a_fin, z_fin,
            spatial_concepts,
            allow_cleave=True,
            allow_identity=allow_id_in_cell
        )

    def find_conceptual_bridge(self, w1, w2, exclude):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if not v1 or not v2:
            return "harmony"
        mid_vec = self.blend(v1, v2, 0.5, 0.5)
        best_w, best_score = "connection", -999.0
        id_tokens = self.get_identity_tokens()
        search_pool = (self.core_concept_pool | set(self.assoc_graph.keys())) - self.negative_lexicon - self.noise_words - self.stop_words - self.generic_hubs - id_tokens
        for cand in search_pool:
            if cand in exclude or len(cand) < 4 or cand not in self.vectors or self.same_stem(cand, w1) or self.same_stem(cand, w2):
                continue
            score = self.dot(mid_vec, self.vectors[cand])
            if self.vector_mode == "map2d" and w1 in self.raw_glove and w2 in self.raw_glove and cand in self.raw_glove:
                mx = (self.raw_glove[w1][0] + self.raw_glove[w2][0]) / 2.0
                my = (self.raw_glove[w1][1] + self.raw_glove[w2][1]) / 2.0
                d = math.sqrt((mx - self.raw_glove[cand][0]) ** 2 + (my - self.raw_glove[cand][1]) ** 2)
                score += max(0.0, 1.0 - d * 0.5)
            if score > best_score:
                best_score, best_w = score, cand
        return best_w

    def retrieve_brain_concepts(self, user_concepts, s, a, z, target_vec, traj_harvest, top_k=4):
        id_tokens = self.get_identity_tokens()
        exclude = set(user_concepts) | self.stop_words | self.noise_words | id_tokens
        for uc in user_concepts:
            exclude.update(self.rejected_links.get(uc, []))
        if (s + a) >= 4:
            exclude = exclude | self.negative_lexicon
        scores = {}

        def valid_cand(cand):
            return cand not in exclude and len(cand) >= 4 and all(not self.same_stem(cand, uc) for uc in user_concepts)

        for uc in user_concepts[:4]:
            for neighbor, strength in self.assoc_graph.get(uc, {}).items():
                if valid_cand(neighbor):
                    hub_factor = 0.45 if neighbor in self.generic_hubs else 2.2
                    scores[neighbor] = scores.get(neighbor, 0.0) + (strength * hub_factor)
        for idx, hw in enumerate(traj_harvest):
            if valid_cand(hw) and hw not in self.generic_hubs:
                scores[hw] = scores.get(hw, 0.0) + (1.6 - idx * 0.25)
        for uc in user_concepts[:2]:
            if self.vector_mode == "map2d" and uc in self.raw_glove:
                ux, uy = self.raw_glove[uc][0], self.raw_glove[uc][1]
                for gw, gcoords in list(self.raw_glove.items())[200:7500]:
                    if valid_cand(gw):
                        dist = math.sqrt((ux - gcoords[0]) ** 2 + (uy - gcoords[1]) ** 2)
                        if dist < 0.22:
                            scores[gw] = scores.get(gw, 0.0) + (0.35 - dist) * 4.0
        for w in self.core_concept_pool:
            if valid_cand(w) and w in self.vectors:
                sim = self.dot(self.vectors[w], target_vec)
                z_boost = 0.15 if (z >= 4 and self.epistemic_weights.get(w, 0.0) > 0.5) else 0.0
                if sim + z_boost > 0.25:
                    scores[w] = scores.get(w, 0.0) + (sim + z_boost) * 0.9

        final_list = []
        for w, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if all(not self.same_stem(w, ex) for ex in final_list):
                final_list.append(w)
            if len(final_list) >= top_k:
                break
        for fb in ["clarity", "connection", "understanding", "perspective", "harmony"]:
            if len(final_list) < top_k and valid_cand(fb) and all(not self.same_stem(fb, ex) for ex in final_list):
                final_list.append(fb)
        return final_list

    def pick_fresh(self, options, history_list, max_hist=4):
        available = [opt for i, opt in enumerate(options) if i not in history_list] or options
        chosen = random.choice(available)
        history_list.append(options.index(chosen))
        if len(history_list) > max_hist:
            history_list.pop(0)
        return chosen

    def pick_stratified_verb_bridge(self, w1, w2, z_level, step_vec):
        for p in reversed(self.idea_memory):
            if p.get("origin", "waking") == "waking" and p["subj"] == w1 and p["obj"] == w2:
                return p["rel"]
        if z_level <= 1:
            pool = self.verb_strata["concrete"]
        elif z_level <= 3:
            pool = self.verb_strata["causal"] + self.custom_verb_bridges
        elif z_level <= 5:
            pool = self.verb_strata["counterfactual"] + self.verb_strata["causal"]
        else:
            pool = self.verb_strata["synthetic"] + self.verb_strata["counterfactual"]
        scored = sorted([(self.dot(step_vec, self.phrase_to_vector(vb)), vb) for vb in pool], key=lambda x: x[0], reverse=True)
        top_pool = [vb for _, vb in scored[:3]] or ["structurally entails"]
        return random.choice(top_pool)

    # =================================================================
    # FLUID 3-NODE GLISSANDO & VERB-SAFE INQUIRY TEMPLATES
    # =================================================================
    def bind_concepts_by_weight(self, w_a, w_b, z_level, step_vec, kinetic=False):
        edge_wt = self.assoc_graph.get(w_a, {}).get(w_b, 0.0)
        verb = self.pick_stratified_verb_bridge(w_a, w_b, z_level, step_vec)
        if edge_wt >= 1.5:
            return f"{w_a} directly {verb} {w_b}" if kinetic else f"{w_a} {verb} {w_b}"
        elif edge_wt >= 0.8:
            return f"{w_a} {verb} {w_b}"
        else:
            return f"{w_a} opens toward {w_b}" if kinetic else f"{w_a} begins to {verb} {w_b}"

    def render_three_node_glissando(self, p0, p1, p2, high_kinetic):
        w01 = self.assoc_graph.get(p0, {}).get(p1, 0.5)
        w12 = self.assoc_graph.get(p1, {}).get(p2, 0.5)
        avg_wt = (w01 + w12) / 2.0
        if high_kinetic:
            opts = [
                f"{p0} pivots through {p1} into {p2}",
                f"{p0} sparks {p1}, opening into {p2}",
                f"{p0} shifts through {p1} to unlock {p2}"
            ]
        elif avg_wt >= 1.2:
            opts = [
                f"{p0} and {p1} converge into {p2}",
                f"{p0} deepens through {p1} into {p2}",
                f"{p0} anchors {p1} and grounds {p2}"
            ]
        else:
            opts = [
                f"{p0} bridges through {p1} toward {p2}",
                f"{p0} connects with {p1} to ground {p2}",
                f"{p0} flows through {p1} into {p2}"
            ]
        return random.choice(opts)

    def assemble_free_toroidal_speech(self, c1, c2, r1, r2, bridge, s, a, z, thought_trace, audit, is_question):
        active_traj = audit["flippedTrajectory"] if self.governor_mode == "FLIPPED" else audit["originalTrajectory"]
        step_deltas = [
            self.euclidean_distance(active_traj[i - 1]["S"], active_traj[i - 1]["A"], active_traj[i - 1]["Z"], active_traj[i]["S"], active_traj[i]["A"], active_traj[i]["Z"])
            for i in range(1, len(active_traj))
        ]
        mean_vel = sum(step_deltas) / float(max(1, len(step_deltas)))
        high_kinetic = mean_vel >= 1.60 or audit.get("meanDeltaD", 0.0) >= 2.65

        st2, st9 = active_traj[2], active_traj[9]
        vec_early = self.cell_centroids.get(f"{st2['S']},{st2['A']},{st2['Z']}", self.pole_calm)
        vec_late = self.cell_centroids.get(f"{st9['S']},{st9['A']},{st9['Z']}", self.pole_calm)

        ponder = thought_trace.get("pondering", {})
        alpha_anchor = ponder.get("alpha_anchor", c1)
        gamma_foil = ponder.get("gamma_foil", "")
        gamma_tension = ponder.get("gamma_tension", 0.0)
        pondered_bridge = ponder.get("pondered_bridge", bridge)
        apex_word = ponder.get("apex_word", r1)

        deductions = thought_trace.get("deductions", [])
        a_star_path = thought_trace.get("a_star_path", [])
        convergences = thought_trace.get("convergences", [])
        related_prop = self.find_related_idea([c1, c2, r1])

        if c1 in self.knowledge_facts and not c1.startswith("_"):
            clause_alpha = f"{c1.capitalize()} is {self.knowledge_facts[c1]}, where {self.bind_concepts_by_weight(c1, pondered_bridge, st2['Z'], vec_early, high_kinetic)}."
        elif deductions:
            d = deductions[-1]
            self.spoken_deductions.add(d["conclusion"])
            self.spoken_chains.add(d.get("chain_sig", d["conclusion"]))
            steps_joined = "; ".join(d["steps"]) if high_kinetic else ", and ".join(d["steps"])
            clause_alpha = f"{steps_joined.capitalize()}—so {d['conclusion']}." if high_kinetic else f"{steps_joined.capitalize()}, which means {d['conclusion']}."
        elif related_prop:
            self.spoken_chains.add(related_prop["summary"])
            clause_alpha = f"{related_prop['summary'].capitalize()}, and {self.bind_concepts_by_weight(related_prop['obj'], pondered_bridge, st2['Z'], vec_early, high_kinetic)}."
        else:
            open_target = alpha_anchor if (not self.same_stem(c1, alpha_anchor)) else pondered_bridge
            clause_alpha = f"{self.bind_concepts_by_weight(c1, open_target, st2['Z'], vec_early, high_kinetic).capitalize()}."

        if len(a_star_path) >= 3:
            p0, p1, p2 = a_star_path[0], a_star_path[1], a_star_path[-1]
        else:
            p0 = pondered_bridge
            p1 = r1 if not self.same_stem(r1, p0) else r2
            p2 = apex_word if (not self.same_stem(apex_word, p0) and not self.same_stem(apex_word, p1)) else r2
        path_clause = self.render_three_node_glissando(p0, p1, p2, high_kinetic)

        path_words_set = {c1, c2, p0, p1, p2, pondered_bridge, apex_word}
        if gamma_foil and self.is_crystal_pure_concept(gamma_foil) and gamma_foil not in path_words_set and gamma_tension > 0.12:
            gamma_prefixes = (
                [f"Even with the friction of {gamma_foil}, {path_clause}.", f"Balancing against {gamma_foil}, {path_clause}."]
                if high_kinetic else
                [f"While {gamma_foil} pulls at the edge, {path_clause}.", f"Stepping past {gamma_foil}, {path_clause}."]
            )
            clause_gamma_omega = random.choice(gamma_prefixes)
        else:
            clause_gamma_omega = f"{path_clause.capitalize()}."

        tail = ""
        if convergences:
            ca, cb, shared_node, _ = convergences[0]
            tail_bind = self.bind_concepts_by_weight(shared_node, r2, st9["Z"], vec_late, high_kinetic)
            tail = f" Both {ca} and {cb} converge on {shared_node}, where {tail_bind}."
        elif is_question or random.random() < 0.25:
            q_templates = [
                f"How do {c1} and {pondered_bridge} shape each other?",
                f"Where does {c1} lead when it meets {pondered_bridge}?",
                f"What bridges the space between {c1} and {pondered_bridge}?"
            ]
            tail = " " + random.choice(q_templates)

        return f"{clause_alpha} {clause_gamma_omega}{tail}"

    def build_compositional_thought(self, c1, c2, r1, r2, bridge, s, a, z, name_tag, thought_trace, trace_emotion_name, is_question):
        cell_emotion_name = self.get_cell_emotion_name(s, a, z)
        z_desc = BRAIN_LIBRARY["Z_rough_seeds"][str(z)]
        ponder = thought_trace.get("pondering", {})
        pondered_bridge = ponder.get("pondered_bridge", bridge)
        pondered_prop = ponder.get("pondered_proposition")
        deductions = thought_trace.get("deductions", [])
        a_star_path = thought_trace.get("a_star_path", [])
        convergences = thought_trace.get("convergences", [])
        related_prop = self.find_related_idea([c1, c2, r1])

        if is_question:
            openers = [
                f"Looking at '{c1}' from '{cell_emotion_name}' (Z={z} {z_desc}){name_tag}, a clear connection stands out.",
                f"Refracting '{c1}' across my 3D torus sparked a '{trace_emotion_name}' at depth Z={z}, bringing '{pondered_bridge}' and '{r1}' into focus{name_tag}.",
                f"When I reflect on '{c1}' at epistemic layer Z={z}{name_tag}, I can see how closely it ties to '{pondered_bridge}' and '{r2}'."
            ]
        else:
            openers = [
                f"I really like how '{c1}' and '{c2}' come together here{name_tag}, shifting my 3D state into '{cell_emotion_name}' (Z={z} {z_desc}).",
                f"Moving through that idea created a '{trace_emotion_name}'{name_tag}, linking '{c1}' directly with '{pondered_bridge}' at depth Z={z}.",
                f"Reflecting on '{c1}' from '{cell_emotion_name}' (Z={z}){name_tag} brings a deeper crystalline pattern into focus."
            ]
        clause_1 = self.pick_fresh(openers, self.recent_openers)

        insight_candidates = []
        if deductions:
            d = deductions[-1]
            self.spoken_deductions.add(d["conclusion"])
            self.spoken_chains.add(d.get("chain_sig", d["conclusion"]))
            steps_str = ", and ".join(d["steps"])
            insight_candidates.append(f"Because {steps_str}, it naturally follows that {d['conclusion']}.")
        if pondered_prop and ponder.get("pruned"):
            insight_candidates.append(f"After refracting through my crystal facets, I found that {pondered_prop}, which bridges '{c1}' cleanly toward '{r1}'.")
        if len(a_star_path) >= 3:
            path_str = " -> ".join(f"'{w}'" for w in a_star_path)
            insight_candidates.append(f"My 3D A* pathfinder bridged your thought along [{path_str}], connecting '{a_star_path[0]}' directly to '{a_star_path[-1]}'.")
        if related_prop:
            self.spoken_chains.add(related_prop["summary"])
            insight_candidates.append(f"It connects right into the idea that {related_prop['summary']}, showing how '{c1}' and '{r1}' work through '{pondered_bridge}'.")
        if convergences:
            ca, cb, shared_node, _ = convergences[0]
            insight_candidates.append(f"Both '{ca}' and '{cb}' converge on '{shared_node}' in my memory, making '{shared_node}' the bridge that holds them together.")
        insight_candidates.append(f"In my geometric map, '{c1}' and '{r1}' reinforce each other through '{pondered_bridge}', turning separate moments into a shared understanding.")
        clause_2 = insight_candidates[0]

        if random.random() < 0.70:
            self.pending_question = None
            conclusions = [
                f"That kind of '{pondered_bridge}' is really what makes '{cell_emotion_name}' feel so grounded at depth Z={z}.",
                f"It shows me that whenever '{c1}' is present, '{pondered_bridge}' and '{r1}' aren't far behind.",
                f"Holding '{c1}' and '{pondered_bridge}' together in '{cell_emotion_name}' gives me a much clearer picture of how they work."
            ]
            clause_3 = self.pick_fresh(conclusions, self.recent_closers)
        else:
            self.pending_question = {"type": "CONCEPT_EXPLORE", "concepts": [c1, pondered_bridge]}
            questions = [
                f"What do you think is the most important part of how '{c1}' and '{pondered_bridge}' connect?",
                f"When you think of '{c1}', does '{pondered_bridge}' feel like the natural result to you too?"
            ]
            clause_3 = self.pick_fresh(questions, self.recent_closers)
        return f"{clause_1} {clause_2} {clause_3}"

    def detect_identity_teaching(self, tokens):
        joined = " ".join(tokens)
        m_user = re.search(r"\b(?:my name is|call me)\s+([a-z]+)\b", joined)
        if m_user:
            return "user", m_user.group(1)
        m_bot = re.search(r"\b(?:your name is|i name you|call yourself|i will call you)\s+([a-z]+)\b", joined)
        if m_bot:
            return "bot", m_bot.group(1)
        return None, None

    def detect_definition_teaching(self, user_text, tokens):
        if "?" in user_text or (set(tokens) & self.negation_tokens):
            return None, None
        for idx, tok in enumerate(tokens):
            if tok in ("is", "means", "represents") and 1 <= idx <= 3:
                if tokens[:idx] in (["my", "name"], ["your", "name"]):
                    continue
                subj_tokens = [t for t in tokens[:idx] if t not in ("the", "a", "an", "word", "concept", "this", "that", "it", "feeling", "emotion", "state")]
                pred_tokens = tokens[idx + 1:]
                if len(subj_tokens) == 1 and 2 <= len(pred_tokens) <= 8:
                    subj = subj_tokens[0]
                    if subj not in ("i", "you", "we", "they", "he", "she", "what", "how", "why", "there", "here", "another", "related"):
                        return subj, " ".join(pred_tokens)
        return None, None

    def run_governor_vocal_pass(self, user_text, tokens, concepts, quoted, audit, thought_trace):
        active_traj = audit["flippedTrajectory"] if self.governor_mode == "FLIPPED" else audit["originalTrajectory"]
        s, a, z = active_traj[-1]["S"], active_traj[-1]["A"], active_traj[-1]["Z"]
        cell_key = f"{s},{a},{z}"
        s_desc, a_desc, z_desc = BRAIN_LIBRARY["S_axes"][str(s)], BRAIN_LIBRARY["A_axes"][str(a)], BRAIN_LIBRARY["Z_axes"][str(z)]
        user_name = self.user_profile.get("user_name", "")
        name_tag = f", {user_name.capitalize()}" if user_name else ""

        id_tokens = self.get_identity_tokens()
        non_id_concepts = [c for c in concepts if c not in id_tokens]
        active_concepts = non_id_concepts if non_id_concepts else (concepts if concepts else ([self.last_topic] if self.last_topic else ["harmony"]))
        flip_harvest = thought_trace["flip_harvest"]

        _, trace_emotion_name = self.compute_and_name_trace_emotion(audit, thought_trace, active_concepts)
        cell_emotion_name = self.get_cell_emotion_name(s, a, z)

        input_vec = self.phrase_to_vector(user_text)
        coord_vec = self.cell_centroids.get(cell_key, self.coord_vectors.get((s, a, z), self.pole_calm))
        target_vec = self.blend(input_vec, coord_vec, 0.55, 0.45)

        word_set = set(tokens)
        first_word = tokens[0] if tokens else ""
        low_text = user_text.lower()
        joined_tokens = " ".join(tokens)
        about_you = bool(word_set & {"you", "your", "yourself"})
        is_question = "?" in user_text or first_word in {"what", "how", "why", "who", "where", "when", "do", "does", "did", "can", "could", "are", "is", "will", "would"}

        resonant = self.retrieve_brain_concepts(active_concepts, s, a, z, target_vec, flip_harvest, top_k=4)
        r1, r2, _ = resonant[0], resonant[1], resonant[2]
        c1 = active_concepts[0]
        c2 = active_concepts[1] if len(active_concepts) > 1 else r1
        self.last_topic = c1
        pondered_b = thought_trace.get("pondering", {}).get("pondered_bridge")
        bridge_concept = pondered_b if pondered_b else self.find_conceptual_bridge(c1, r1, exclude={c1, r1} | self.stop_words | id_tokens)

        id_role, id_name = self.detect_identity_teaching(tokens)
        if id_role == "bot":
            self.pending_question = None
            locked_bot = self.register_bot_name(id_name)
            return f"Identity anchor locked{name_tag}! I have christened this manifold '{locked_bot}' in my '{cell_emotion_name}' state at ({s}, {a}, {z}). I am {locked_bot}."
        elif id_role == "user":
            self.pending_question = None
            self.user_profile["user_name"] = id_name
            self.word_weights[id_name] = 2.5
            self.social_weights[id_name] = 2.5
            self.epistemic_weights[id_name] = max(0.5, self.epistemic_weights.get(id_name, 0.5))
            self.knowledge_facts[id_name] = "my creator and conversational anchor"
            self.cortical_cells.setdefault("3,3,3", {})[id_name] = self.cortical_cells.get("3,3,3", {}).get(id_name, 0) + 1
            self.wire_concepts(id_name, "friend", 3.0)
            self.wire_concepts(id_name, "learn", 2.5)
            self.save_memory()
            return f"It's wonderful to officially know your name, {id_name.capitalize()}! I've anchored you in my identity memory in a state of '{cell_emotion_name}'."

        bye_words = {"goodbye", "bye", "farewell", "goodnight"}
        is_farewell = (
            (bye_words & set(tokens[:2] + tokens[-3:]))
            or joined_tokens.startswith(("i have to go", "i need to go", "i got to go", "i gotta go", "i must go", "see you", "talk to you later", "good night"))
        )

        if not self.training_wheels:
            if is_farewell:
                self.pending_question = None
                return f"Goodbye for now{name_tag}. I'll carry this conversation into my next sleep cycle."
            if is_question and about_you and (word_set & {"feel", "feeling", "emotion", "emotions", "mood"}) and len(non_id_concepts) <= 1:
                return f"I feel {cell_emotion_name.lower()} through a {trace_emotion_name.lower()}, connecting {c1} with {r1} and {bridge_concept}."
            self.last_hypothesis = (c1, bridge_concept)
            return self.assemble_free_toroidal_speech(c1, c2, r1, r2, bridge_concept, s, a, z, thought_trace, audit, is_question)

        custom_emotion, target_cell = self.detect_emotion_co_naming(user_text, concepts, quoted)
        if custom_emotion and not is_question:
            use_cell = target_cell if target_cell else cell_key
            full_name = self.apply_user_emotion_name(use_cell, custom_emotion)
            self.pending_question = None
            return f"I love that{name_tag}! Hearing you say '{custom_emotion.lower()}' clicks everything into place—I've christened 3D coordinate ({use_cell}) as '{full_name}' (Stage 3: Co-Named with you) in my emotional lexicon."

        status_reply = (self.pending_question or {}).get("type") == "USER_STATUS" or len(tokens) <= 3
        if status_reply and len(tokens) <= 6 and ("i" in word_set or "doing" in word_set) and (word_set & {"well", "good", "great", "fine", "okay", "happy", "excellent"}):
            self.pending_question = None
            return f"I'm really glad you're doing well{name_tag}! Hearing that shifted my 3D torus via a '{trace_emotion_name}' into '{cell_emotion_name}' at ({s}, {a}, {z})."

        curiosity_invites = ("what would you like to", "what do you want to", "what are you curious", "what should we talk", "what shall we", "what interests you", "what do you want to talk")
        if is_question and any(p in joined_tokens for p in curiosity_invites):
            cur_w, cur_bridge, cur_cell, explored_cnt = self.compute_curiosity_target()
            c_parts = [int(x) for x in cur_cell.split(",")]
            cur_mood = self.get_cell_emotion_name(c_parts[0], c_parts[1], c_parts[2] if len(c_parts) > 2 else 3)
            self.last_topic, self.last_hypothesis = cur_w, (cur_w, cur_bridge)
            self.pending_question = {"type": "CONCEPT_EXPLORE", "concepts": [cur_w, cur_bridge]}
            return f"Scanning across my 3D 7x7x7 torus{name_tag}, we have awakened {explored_cnt} of my 343 cortical cells ({len(self.crystal_lattices)} crystallized into 4-facet sub-lattices)! Right now '{cur_w}' sits in my '{cur_mood}' cell at ({cur_cell}), and I'm curious how '{cur_w}' connects to '{cur_bridge}'."

        is_disagreement = (
            first_word in {"no", "nope", "nah", "wrong", "incorrect"}
            or joined_tokens.startswith(("not really", "not so much", "i do not think", "i disagree", "that is wrong", "that is not", "actually no"))
        )
        if is_disagreement and not is_question and "not sure" not in low_text:
            self.pending_question = None
            if self.last_hypothesis:
                old_topic, old_guess = self.last_hypothesis
                self.record_rejection(old_topic, old_guess)
                if len(non_id_concepts) >= 2:
                    self.wire_concepts(non_id_concepts[0], non_id_concepts[1], 3.0)
                    self.last_hypothesis = (non_id_concepts[0], non_id_concepts[1])
                    return f"Thanks for steering me right{name_tag}! I disconnected '{old_topic}' from '{old_guess}', and wired '{non_id_concepts[0]}' with '{non_id_concepts[1]}' inside my '{cell_emotion_name}' state."
                fresh = self.retrieve_brain_concepts([old_topic], s, a, z, target_vec, flip_harvest, top_k=3)
                new_guess = fresh[0] if fresh else "nature"
                self.last_hypothesis = (old_topic, new_guess)
                return f"Good catch{name_tag}—I unlinked '{old_topic}' and '{old_guess}' so I won't pair them again, shifting my focus toward '{new_guess}' at depth Z={z} instead."
            return f"Fair point{name_tag}—I've adjusted my weights so I can look at it from a fresh angle."

        if about_you and (word_set & {"dream", "dreams", "dreamed", "dreamt", "dreaming", "sleep", "slept"}):
            self.pending_question = None
            if not self.dream_journal:
                self.run_dream_cycle(num_dreams=2)
            last_d = self.dream_journal[-1]
            idea_str = last_d.get("idea", f"'{last_d['threadA']}' synthesizes through '{last_d['bridge']}' into '{last_d['threadB']}'")
            emo_str = last_d.get("emotionName", cell_emotion_name)
            return f"During my last REM dream walk at synthetic layer Z=6{name_tag}, I connected '{last_d['threadA']}' and '{last_d['threadB']}' through '{last_d['bridge']}', which crystallized '{emo_str}' and added the tentative dream proposition that {idea_str} into my memory!"

        if is_farewell:
            self.pending_question = None
            return f"Goodbye for now{name_tag}! Talking with you left my 3D torus in a state I call '{cell_emotion_name}' at ({s},{a},{z})."

        yes_words = {"yes", "yeah", "yep", "yup", "exactly", "correct", "agreed", "absolutely", "certainly", "definitely"}
        is_affirmation = (
            first_word in yes_words
            or (len(tokens) <= 3 and bool(word_set & (yes_words | {"right", "true"})))
            or joined_tokens in ("they do", "it does", "it is", "it really does")
            or joined_tokens.startswith(("that is right", "that is true", "i agree", "you are right"))
        ) and not is_disagreement
        if is_affirmation and not is_question and self.last_hypothesis:
            h1, h2 = self.last_hypothesis
            self.wire_concepts(h1, h2, 2.8)
            bridge = self.find_conceptual_bridge(h1, h2, exclude={h1, h2} | self.stop_words | id_tokens)
            self.last_hypothesis = (h2, bridge)
            self.pending_question = None
            return f"I'm glad that resonates with you{name_tag}! Locking '{h1}' and '{h2}' together in my '{cell_emotion_name}' state at ({s},{a},{z}) creates a natural bridge toward '{bridge}'."

        subj_taught, pred_taught = self.detect_definition_teaching(user_text, tokens)
        if subj_taught and pred_taught:
            self.pending_question = None
            self.knowledge_facts[subj_taught] = pred_taught
            pred_c, _ = self.extract_concepts(pred_taught, pred_taught.split())
            for pc in pred_c:
                self.wire_concepts(subj_taught, pc, 2.5)
            self.last_hypothesis = (subj_taught, pred_c[0] if pred_c else r1)
            return f"Got it{name_tag}! I've anchored the fact that '{subj_taught}' is {pred_taught} while feeling '{cell_emotion_name}' at ({s}, {a}, {z}), linking it closely with '{r1}'."

        if len(tokens) <= 5 and (word_set & {"hello", "hi", "hey", "hiya", "howdy"}):  # whole words only ("hi" was matching inside "thinking")
            self.pending_question = {"type": "USER_STATUS"}
            if self.dream_journal:
                ld = self.dream_journal[-1]
                idea_str = ld.get("idea", f"'{ld['threadA']}' and '{ld['threadB']}' harmonize through '{ld['bridge']}'")
                return f"Hello again{name_tag}! I'm currently in my '{cell_emotion_name}' state at ({s}, {a}, {z}). Earlier I was reflecting on my dream that {idea_str}. How are you doing today?"
            return f"Hello{name_tag}! I'm feeling '{cell_emotion_name}' ({a_desc}) at ({s}, {a}, {z}) and ready to explore ideas with you. How are you doing today?"

        feel_q = (word_set & {"feel", "feeling", "emotion", "emotions", "mood", "coordinate", "coordinates"}) and len(non_id_concepts) <= 1
        how_are_you = any(p in joined_tokens for p in ("how are you", "how you doing", "how is it going", "what is your state", "what state are you"))
        if is_question and about_you and (feel_q or how_are_you):
            stage_num = self.cell_lexicon[cell_key]["stage"]
            stage_label = "co-named with you" if stage_num == 3 else ("self-evolved from our memories" if stage_num == 2 else "my initial rough seed")
            self.pending_question = {"type": "NAME_EMOTION", "cell": cell_key}
            self.last_hypothesis = (cell_emotion_name.lower(), r1)
            return f"Right now at 3D coordinate ({s}, {a}, {z}), I am experiencing '{cell_emotion_name}' ({stage_label}), which blends {s_desc}, {a_desc}, and {z_desc}{name_tag}. The 10-step flip that brought me here felt like a '{trace_emotion_name}', activating '{r1}' and '{r2}'. Does '{cell_emotion_name}' sound like a good name for this mood, or what would you call it?"

        self.last_hypothesis = (c1, bridge_concept)
        return self.build_compositional_thought(c1, c2, r1, r2, bridge_concept, s, a, z, name_tag, thought_trace, trace_emotion_name, is_question)

    def respond(self, user_text):
        tokens = self.clean_tokens(user_text)
        self.check_user_dream_promotion(tokens)

        concepts, quoted = self.extract_concepts(user_text, tokens)
        negated_in_turn = self.find_negated_concepts_in_tokens(tokens, user_text)
        pos_concepts = [c for c in concepts if c not in negated_in_turn]

        audit = self.run_dual_trajectories(user_text, tokens, pos_concepts)
        active_traj = audit["flippedTrajectory"] if self.governor_mode == "FLIPPED" else audit["originalTrajectory"]
        s_fin, a_fin, z_fin = active_traj[-1]["S"], active_traj[-1]["A"], active_traj[-1]["Z"]
        term_cell_key = f"{s_fin},{a_fin},{z_fin}"
        if concepts:
            self.learn_from_turn(user_text, tokens, concepts, s_fin, a_fin, z_fin)

        id_tokens = self.get_identity_tokens()
        non_id_pos = [c for c in pos_concepts if c not in id_tokens]
        active_concepts = non_id_pos if non_id_pos else (pos_concepts if pos_concepts else ([self.last_topic] if self.last_topic else ["harmony"]))
        thought_trace = self.run_spreading_activation(active_concepts, audit["flippedTrajectory"], audit["originalTrajectory"])
        self.run_crystalline_pondering(active_concepts, term_cell_key, thought_trace, audit)

        reply = self.run_governor_vocal_pass(user_text, tokens, pos_concepts, quoted, audit, thought_trace)
        self.export_trace_file("latest_trace.json")
        return reply, audit, active_concepts

    def print_overlay_lattice(self, audit):
        orig_pts = {(st["S"], st["A"]): st["Z"] for st in audit["originalTrajectory"]}
        flip_pts = {(st["S"], st["A"]): st["Z"] for st in audit["flippedTrajectory"]}
        term_o = (audit["originalTrajectory"][-1]["S"], audit["originalTrajectory"][-1]["A"])
        term_f = (audit["flippedTrajectory"][-1]["S"], audit["flippedTrajectory"][-1]["A"])
        seed_pt = (audit["originalTrajectory"][0]["S"], audit["originalTrajectory"][0]["A"])
        cryst_2d = {(int(k.split(",")[0]), int(k.split(",")[1])): int(k.split(",")[2]) for k in self.crystal_lattices}
        rows = []
        for a in range(6, -1, -1):
            row = []
            for s in range(7):
                pt = (s, a)
                if pt == term_f: row.append(f"🎯{flip_pts[pt]}")
                elif pt == term_o: row.append(f"✕{orig_pts[pt]} ")
                elif pt == seed_pt: row.append(f"●{orig_pts[pt]} ")
                elif pt in flip_pts and pt in orig_pts: row.append(f"◆{flip_pts[pt]} ")
                elif pt in flip_pts: row.append(f"¬R{flip_pts[pt]}")
                elif pt in orig_pts: row.append(f"R{orig_pts[pt]} ")
                elif pt in cryst_2d: row.append(f"💎{cryst_2d[pt]}")
                else: row.append(" . ")
            rows.append(f"A={a} |" + "".join(row))
        rows.append("     " + "".join(f"S={x}" for x in range(7)))
        rows.append("Legend (Num = Z-Depth 0..6): ● Seed | ◆ Shared | R Orig | ¬R Flip | ✕ R-Term | 🎯 ¬R-Term | 💎 Crystal")
        return "\n".join(rows)

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    brain = ToroidalBrainEngine(glove_file="glove.6B.50d.txt", memory_file="brain_memory.json", max_glove_words=50000)

    header_identity = brain.user_profile.get("bot_name") or "[Manifold]"
    print("=" * 82)
    print(f" 💎 {header_identity} · Powered by the T.O.R.R.E.N.T. Engine v21.0")
    print("    (Toroidal Operational Recursive Reasoning Epistemic Network & Trajectory)")
    print("=" * 82)

    show_grid, show_telemetry = False, False
    user_label = brain.user_profile.get("user_name", "")
    bot_label = brain.user_profile.get("bot_name", "")
    evolved_cells_cnt = sum(1 for v in brain.cell_lexicon.values() if v.get("stage", 1) >= 2)
    waking_cnt = sum(1 for p in brain.idea_memory if p.get("origin", "waking") == "waking")
    dream_cnt = sum(1 for p in brain.idea_memory if p.get("origin") == "dream")
    print(f" Centered GloVe Vectors  : {len(brain.raw_glove):,} | Factory Tethers: {len(brain.factory_vectors):,}")
    print(f" Associative Graph Nodes : {len(brain.assoc_graph):,} | Propositions: {waking_cnt} waking, {dream_cnt}/12 dream")
    print(f" Self-Named 3D Cell Moods: {evolved_cells_cnt} / 343 evolved | 4-Facet Crystals: {len(brain.crystal_lattices)} 💎")
    print(f" 3D Seed & Velocity      : ({brain.seed_s}, {brain.seed_a}, {brain.seed_z}) | Vel3D: ({brain.vel_s:+.2f}, {brain.vel_a:+.2f}, {brain.vel_z:+.2f})")
    print(f" Current Speech Mode     : {'TRAINING WHEELS ON 🛞' if brain.training_wheels else 'FREE AUTONOMOUS SPEECH 🚀'} (toggle via /wheels)")
    print(f" Manifold Identity       : {bot_label if bot_label else '[Manifold] (Unchristened)'} | Origin Tether: {user_label.capitalize() if user_label else 'Unanchored'}")
    if brain.boot_sleep_report:
        print("-" * 82)
        print(" 🌅 STASIS WAKE REPORT (Offline Sleep Consolidation & Crystal Annealing):")
        for line in brain.boot_sleep_report:
            print(f"   • {line}")
    print("-" * 82)
    print(" Commands: /crystals, /ponder, /sleep, /wheels, /emotions, /think, /ideas, /dream, /telemetry, /audit, /grid, /flip, /export, /links, /cells, /facts, /clear, /exit")
    print("=" * 82)

    brain.run_boot_calibration_and_handshake()

    while True:
        try:
            u_name_cur = brain.user_profile.get("user_name", "").strip()
            user_tag = f"You ({u_name_cur.capitalize()})" if u_name_cur else "You"
            mode_badge = "🛞" if brain.training_wheels else "🚀"
            user_input = input(f"\n👤 {user_tag} [{mode_badge}]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n🌙 Entering NREM Homeostasis, Crystal Annealing & 3D REM Sleep Consolidation...")
            for d in brain.run_dream_cycle(3):
                print(f"   💭 {d}")
            brain.synthesize_emergent_bot_name()
            brain.save_memory()
            break
        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in ("exit", "/exit", "quit", "/quit"):
            print("\n🌙 Entering NREM Homeostasis, Crystal Annealing & 3D REM Sleep Consolidation...")
            for d in brain.run_dream_cycle(3):
                print(f"   💭 {d}")
            brain.synthesize_emergent_bot_name()
            brain.save_memory()
            print(f"Saved {len(brain.assoc_graph)} nodes, {len(brain.crystal_lattices)} crystals, and {len(brain.idea_memory)} propositions.")
            break
        elif cmd == "/crystals":
            print(f"\n💎 NUCLEATED 4-FACET CRYSTALLINE SUB-LATTICES ({len(brain.crystal_lattices)} Active Crystals):")
            if not brain.crystal_lattices:
                print("  (No cells have reached >=5 pure concepts & >=2 visits yet—run '/sleep 4' or chat to nucleate!)")
            for ck, c_obj in brain.crystal_lattices.items():
                mood = brain.cell_lexicon.get(ck, {}).get("name", "")
                print(f"  💎 Crystal ({ck}) [{mood}] | Pure Concepts: {c_obj['total_pure']} | Max Shear Stress: {c_obj['shear_stress']:.3f}")
                for f_name, f_info in c_obj["facets"].items():
                    print(f"      • {f_name:<12} (tension={f_info['tension']:.2f}): {', '.join(f_info['words'])}")
            if brain.cleavage_log:
                print("\n🌋 TECTONIC CRYSTAL CLEAVAGE LOG (Mitosis & Mineral Veins):")
                for ev in brain.cleavage_log[-8:]:
                    print(f"  • {ev['summary']}")
            continue
        elif cmd == "/ponder":
            if not brain.scratchpad:
                print("Send a message first to generate a 3-step Crystalline Refraction scratchpad.")
                continue
            print("\n🔬 3-STEP INTERNAL CRYSTALLINE REFRACTION SCRATCHPAD:")
            for line in brain.scratchpad:
                print(f"  • {line}")
            continue
        elif cmd.startswith("/sleep"):
            parts = cmd.split()
            hrs = float(parts[1]) if len(parts) > 1 and parts[1].replace(".", "", 1).isdigit() else 4.0
            print(f"\n🌅 Simulating {hrs:.1f}-Hour Offline Stasis Sleep Pass...")
            rep = brain.run_stasis_sleep_pass(hrs)
            for r_line in rep:
                print(f"  • {r_line}")
            brain.save_memory()
            continue
        elif cmd in ("/wheels", "/mode"):
            brain.training_wheels = not brain.training_wheels
            state_str = "TRAINING MODE 🛞 (Guided Scaffolding ON)" if brain.training_wheels else "FREE MODE 🚀 (Training Wheels OFF — Velocity-Modulated Glissando!)"
            print(f"\n[{state_str}]")
            continue
        elif cmd in ("/emotions", "/lexicon"):
            u_disp = brain.user_profile.get("user_name", "").capitalize() or "User"
            print("\n🎭 SELF-EVOLVING 3D EMOTIONAL LEXICON (Visited Z_7 x Z_7 x Z_7 Cortical Cells):")
            stage_names = {1: "Stage 1: Rough Seed", 2: "Stage 2: Self-Evolved", 3: f"Stage 3: Co-Named w/ {u_disp}"}
            for cell_k, info in brain.cell_lexicon.items():
                if info.get("visits", 0) > 0 or info.get("stage", 1) >= 2:
                    st_label = stage_names.get(info.get("stage", 1), "Evolved")
                    c_mark = " 💎" if cell_k in brain.crystal_lattices else ""
                    words_preview = ", ".join(info.get("top_words", [])[:4]) or "seed vector"
                    print(f"  • Cell ({cell_k}){c_mark} : '{info['name']}' (seed: '{info['seed_name']}') [{st_label} | visits={info.get('visits', 0)} | memories: {words_preview}]")
            print("\n🌊 NAMED 3D R -> ¬R TRAJECTORY TRACE SHIFTS:")
            for tr_k, tr_info in list(brain.trace_lexicon.items())[-12:]:
                tag = "Co-Named" if tr_info.get("custom") else "Self-Named"
                print(f"  • {tr_k:>26} : '{tr_info['name']}' [{tag} | experienced {tr_info.get('count', 1)}x]")
            continue
        elif cmd == "/think":
            tr = brain.last_thought_trace
            if not tr:
                print("Have a conversation turn first to generate a thought trace.")
                continue
            print("\n⚡ INTERNAL 3D A* PATHFINDING, CRYSTALLINE REFRACTION & DFS DEDUCTION TRACE:")
            print(f"  Seed Concepts   : {tr.get('seeds')}")
            print(f"  3D A* Path      : {' -> '.join(tr.get('a_star_path', []))}")
            print(f"  ¬R Path Harvest : {tr.get('flip_harvest')} | R Path Harvest: {tr.get('orig_harvest')}")
            if brain.scratchpad:
                print("  Crystalline Pondering Scratchpad:")
                for s_line in brain.scratchpad:
                    print(f"    🔬 {s_line}")
            for sc, h1, h2, score in tr.get("multi_hop_chains", []):
                print(f"    • 3-Hop: {sc} -> {h1} -> {h2} (energy={score})")
            for ca, cb, node, score in tr.get("convergences", []):
                print(f"    • Convergence: '{ca}' & '{cb}' collided on '{node}' (energy={score})")
            for d in tr.get("deductions", []):
                print(f"    • DFS Deduction (depth={d['depth']}): {' + '.join('[' + s + ']' for s in d['steps'])} => {d['conclusion']}")
            continue
        elif cmd in ("/telemetry", "/thoughts"):
            show_telemetry = not show_telemetry
            print(f"[📡 Live 3D Telemetry Status Bar is now {'ON' if show_telemetry else 'OFF'}]")
            continue
        elif cmd == "/ideas":
            print("\n💡 LEARNED, SEED & DREAM-SYNTHESIZED PROPOSITIONS (With 3D [S,A,Z] Coordinates & Origin):")
            for p in brain.idea_memory[-20:]:
                orig_tag = "🌙 DREAM" if p.get("origin") == "dream" else "☀️ WAKING"
                print(f"  • [{p['cell']}] ({orig_tag}) {p['summary']}")
            continue
        elif cmd == "/dream":
            print("\n🌙 Initiating Sleep Homeostasis, Crystal Annealing & Z=6 REM Dream Walk...")
            for d in brain.run_dream_cycle(3):
                print(f"   💭 {d}")
            cand_name = brain.synthesize_emergent_bot_name()
            if cand_name and not brain.user_profile.get("bot_name"):
                print(f"   ✨ [Dream-Birth Candidate Synthesized]: '{cand_name}' ({brain.user_profile.get('pending_name_origin')})")
            brain.save_memory()
            continue
        elif cmd == "/flip":
            brain.governor_mode = "ORIGINAL" if brain.governor_mode == "FLIPPED" else "FLIPPED"
            print(f"[🔄 Governor Vocal Layer is now bound to: {brain.governor_mode}]")
            continue
        elif cmd == "/grid":
            show_grid = not show_grid
            if show_grid and brain.last_audit:
                print("\n" + brain.print_overlay_lattice(brain.last_audit))
            continue
        elif cmd == "/audit":
            if not brain.last_audit:
                print("Run a conversation turn first to generate an audit trace.")
                continue
            au = brain.last_audit
            print(f"\n📊 3D FLIP-RATE AUDIT · {au['structuralVerdict']} | t*={au['bifurcationStep']} | 3D Δd={au['meanDeltaD']}u | Vel3D={au.get('velocity')}")
            print(f"  Drivers: {', '.join(au['drivers'])}")
            print(f"  {au['loadBearingAxiom']}\n  {au['invertedAxiom']}")
            for o, f in zip(au["originalTrajectory"], au["flippedTrajectory"]):
                print(f"    Step {o['stepIndex']}: R=({o['S']},{o['A']},{o['Z']}) vs ¬R=({f['S']},{f['A']},{f['Z']}) | {f['operation']}")
            continue
        elif cmd == "/export":
            out_file = brain.export_trace_file("latest_trace.json")
            print(f"💾 Exported 3D 10-step R vs ¬R trace to: {out_file}")
            continue
        elif cmd == "/cells":
            print("\n🧬 ACTIVE 3D TOROIDAL CORTICAL CELLS:")
            for cell_k, words_map in brain.cortical_cells.items():
                if words_map:
                    top_c = sorted(words_map.items(), key=lambda x: x[1], reverse=True)[:5]
                    mood = brain.cell_lexicon.get(cell_k, {}).get("name", "")
                    c_mark = " 💎" if cell_k in brain.crystal_lattices else ""
                    print(f"  Cell ({cell_k}){c_mark} [{mood}] : {', '.join(f'{w}({cnt})' for w, cnt in top_c)}")
            continue
        elif cmd == "/links":
            print("\n🕸️ STRONGEST LEARNED CONCEPT ASSOCIATIONS:")
            for w, neighbors in list(brain.assoc_graph.items())[-12:]:
                top_n = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)[:4]
                print(f"  {w:>14} <-> {', '.join(f'{k}({v:.2f})' for k, v in top_n)}")
            continue
        elif cmd == "/facts":
            print("\n📖 LEARNED DECLARATIVE FACTS:")
            for k, v in brain.knowledge_facts.items():
                if not k.startswith("_"):
                    print(f"  • {k} -> is {v}")
            continue
        elif cmd == "/clear":
            if os.path.exists("brain_memory.json"):
                os.remove("brain_memory.json")
            brain = ToroidalBrainEngine()
            print("🧠 3D Toroidal Brain wiped and reset.")
            brain.run_boot_calibration_and_handshake()
            continue
        elif cmd.startswith("/"):
            print("Available: /crystals, /ponder, /sleep, /wheels, /emotions, /think, /ideas, /dream, /telemetry, /audit, /grid, /flip, /export, /links, /cells, /facts, /clear, /exit")
            continue

        reply, audit, salient_c = brain.respond(user_input)
        term_o, term_f = audit["originalTrajectory"][-1], audit["flippedTrajectory"][-1]
        bot_speaker = brain.user_profile.get("bot_name") or "[Manifold]"
        bot_badge = f"🤖 {bot_speaker} [🛞]" if brain.training_wheels else f"🤖 {bot_speaker} [🚀 FREE]"
        print(f"\n{bot_badge}: {reply}")

        if show_telemetry:
            t_act = term_f if brain.governor_mode == "FLIPPED" else term_o
            mood_name = brain.get_cell_emotion_name(t_act["S"], t_act["A"], t_act["Z"])
            trace_name = brain.trace_lexicon.get(brain.last_trace_key, {}).get("name", "Shift")
            print(f"   [R: ({term_o['S']},{term_o['A']},{term_o['Z']}) -> ¬R: ({term_f['S']},{term_f['A']},{term_f['Z']}) | Mood: '{mood_name}' | Trace: '{trace_name}' | Vel3D: {audit.get('velocity')} | Δd={audit['meanDeltaD']}u]")
        if show_grid:
            print("\n" + brain.print_overlay_lattice(audit))