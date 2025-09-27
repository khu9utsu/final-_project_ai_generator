import streamlit as st
import PyPDF2
import docx
import re
import random
import pandas as pd
import base64
import json
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass
import io
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go

# Class untuk merepresentasikan sebuah soal
@dataclass
class Question:
    question_text: str
    options: List[str]
    correct_answer: str
    explanation: str
    question_type: str = "pilihan_ganda"
    difficulty: str = "medium"
    
    # Convert question to dictionary
    def to_dict(self) -> Dict:
        return {
            "question": self.question_text,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "type": self.question_type,
            "difficulty": self.difficulty
        }

# Class untuk memproses materi ajar
class MaterialProcessor:
    def __init__(self):
        self.text_content = ""

    # Ekstrak teks dari file PDF
    def extract_text_from_pdf(self, pdf_file) -> str:
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return ""
    
    # Ekstrak teks dari file DOCX
    def extract_text_from_docx(self, docx_file) -> str:
        try:
            doc = docx.Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading DOCX: {e}")
            return ""
    
    # Ekstrak teks dari file TXT
    def extract_text_from_txt(self, txt_file) -> str:
        try:
            stringio = StringIO(txt_file.getvalue().decode("utf-8"))
            return stringio.read()
        except Exception as e:
            st.error(f"Error reading TXT file: {e}")
            return ""
    
    # Proses file yang diupload dan ekstrak teksnya
    def process_material(self, uploaded_file) -> bool:
        if uploaded_file is None:
            return False
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == "pdf":
            self.text_content = self.extract_text_from_pdf(uploaded_file)
        elif file_extension == "docx":
            self.text_content = self.extract_text_from_docx(uploaded_file)
        elif file_extension == "txt":
            self.text_content = self.extract_text_from_txt(uploaded_file)
        else:
            st.error("Format file tidak didukung. Gunakan PDF, DOCX, atau TXT.")
            return False
        
        # Bersihkan teks dari karakter yang tidak perlu
        self.text_content = self.clean_text(self.text_content)
        if len(self.text_content) < 100:
            st.warning("Teks yang diekstrak terlalu pendek. Pastikan file berisi materi yang cukup.")
            return False
            
        return True
    
    # Hapus karakter khusus dan multiple spaces
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?;:()-]', '', text)
        return text.strip()
    
    def get_key_concepts(self, max_concepts: int = 20) -> List[str]:
        """Ekstrak konsep-konsep penting dari materi"""
        sentences = re.split(r'[.!?]', self.text_content)
        concepts = set()
        for sentence in sentences:
            words = sentence.split()
            for i, word in enumerate(words):
                # Deteksi kemungkinan konsep penting
                cleaned_word = re.sub(r'[^a-zA-Z]', '', word)
                if (len(cleaned_word) > 3 and cleaned_word.isalpha() and 
                    (cleaned_word.istitle() or (i > 0 and words[i-1][-1] == ':'))):
                    concepts.add(cleaned_word.lower())
        
        return list(concepts)[:max_concepts]

# Class untuk menghasilkan soal dengan AI
class AdvancedQuestionGenerator:
    def __init__(self):
        self.generated_questions = []
        self.question_templates = {
            "definition": [
                "Apa yang dimaksud dengan {concept}?",
                "Jelaskan pengertian dari {concept}!",
                "Definisikan konsep {concept}!"
            ],
            "cause_effect": [
                "Apa penyebab dari {concept}?",
                "Apa dampak dari {concept}?",
                "Bagaimana {concept} mempengaruhi proses lainnya?"
            ],
            "comparison": [
                "Bandingkan {concept1} dan {concept2}!",
                "Apa perbedaan antara {concept1} dengan {concept2}?",
                "Apa persamaan {concept1} dan {concept2}?"
            ],
            "application": [
                "Bagaimana cara menerapkan {concept} dalam kehidupan sehari-hari?",
                "Berikan contoh penerapan {concept}!",
                "Aplikasi apa saja yang menggunakan prinsip {concept}?"
            ],
            "simple": [
                "Apa itu {concept}?",
                "Jelaskan {concept} secara singkat!",
                "Apa fungsi dari {concept}?"
            ]
        }
    
    # Generate questions dengan variasi
    def generate_questions_advanced(self, material_text: str, num_questions: int = 10) -> List[Question]:
        sentences = self.extract_meaningful_sentences(material_text)
        concepts = self.extract_key_concepts_advanced(material_text)
        questions = []
        
        # Generate berbagai jenis soal
        for i in range(num_questions):
            question = self.generate_single_question(concepts, sentences, material_text, i)
            if question:
                questions.append(question)
        
        return questions
    
    # Ekstrak kalimat yang bermakna dari teks
    def extract_meaningful_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'[.!?]', text)
        meaningful_sentences = []
        
        for sentence in sentences:
            clean_sentence = sentence.strip()
            words = clean_sentence.split()
            if len(words) >= 5 and len(clean_sentence) > 20:
                meaningful_sentences.append(clean_sentence)
        
        return meaningful_sentences
    
    #Ekstrak konsep kunci
    def extract_key_concepts_advanced(self, text: str) -> List[str]:
        # Cari kata-kata yang sering muncul dan penting
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        word_freq = {}
        # Hanya kata dengan panjang minimal 5 huruf
        for word in words:
            if len(word) > 4:
                word_lower = word.lower()
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        # Urutkan berdasarkan frekuensi dan ambil yang paling sering
        sorted_concepts = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [concept[0] for concept in sorted_concepts[:15]]
    
    #Generate satu soal dengan handling error
    def generate_single_question(self, concepts: List[str], sentences: List[str], material_text: str, question_num: int) -> Question:
        try:
            if not concepts:
                return self.create_question_from_sentence(sentences, question_num)
            
            # Pilih jenis soal berdasarkan nomor soal
            question_types = list(self.question_templates.keys())
            q_type = question_types[question_num % len(question_types)]
            concept = random.choice(concepts)
            template = random.choice(self.question_templates[q_type])
            
            # Handle template dengan multiple concepts
            if "{concept1}" in template and "{concept2}" in template:
                if len(concepts) >= 2:
                    concept1 = concept
                    concept2 = random.choice([c for c in concepts if c != concept1])
                    question_text = template.format(concept1=concept1, concept2=concept2)
                else:
                    template = random.choice(self.question_templates["simple"])
                    question_text = template.format(concept=concept)
            else:
                question_text = template.format(concept=concept)
            
            # Generate options yang realistis
            options, correct_answer, explanation = self.generate_smart_options(
                q_type, concept, concepts, material_text
            )
            
            return Question(
                question_text=question_text,
                options=options,
                correct_answer=correct_answer,
                explanation=explanation,
                question_type="pilihan_ganda",
                difficulty=random.choice(["easy", "medium", "hard"])
            )
            
        except Exception as e:
            st.error(f"Error generating question {question_num + 1}: {e}")
            return self.create_fallback_question(question_num)
    
    # Buat soal dari kalimat jika tidak ada konsep
    def create_question_from_sentence(self, sentences: List[str], question_num: int) -> Question:
        if not sentences:
            return self.create_fallback_question(question_num)
        
        sentence = random.choice(sentences)
        words = sentence.split()
        if len(words) < 3:
            return self.create_fallback_question(question_num)
        
        # Buat soal fill-in-the-blank sederhana
        blank_word = random.choice([w for w in words if len(w) > 4])
        question_text = sentence.replace(blank_word, "______")
        question_text = f"Lengkapi kalimat: {question_text}"
        
        options = [blank_word]
        for _ in range(3):
            options.append(f"Opsi{random.randint(1, 100)}")
        
        random.shuffle(options)
        
        return Question(
            question_text=question_text,
            options=options,
            correct_answer=blank_word,
            explanation=f"Kata '{blank_word}' adalah jawaban yang tepat untuk melengkapi kalimat.",
            difficulty="easy"
        )
    
    # Buat soal fallback jika semua method gagal
    def create_fallback_question(self, question_num: int) -> Question:
        question_text = f"Apa yang Anda pahami tentang materi yang telah dipelajari?"
        options = [
            "Materi sangat jelas dan mudah dipahami",
            "Materi cukup jelas dengan beberapa bagian yang rumit", 
            "Materi cukup sulit dipahami",
            "Materi sangat sulit dan perlu penjelasan lebih"
        ]
        
        return Question(
            question_text=question_text,
            options=options,
            correct_answer=options[0],
            explanation="Soal ini menguji pemahaman umum terhadap materi.",
            difficulty="easy"
        )
    
    # Generate opsi jawaban
    def generate_smart_options(self, q_type: str, concept: str, concepts: List[str], material_text: str) -> Tuple[List[str], str, str]:
        correct_answer = self.generate_correct_answer(q_type, concept, material_text)
        options = [correct_answer]
        
        # Generate distractor yang masuk akal
        distractors = self.generate_plausible_distractors(q_type, concept, concepts, material_text)
        
        # Tambahkan distractor hingga 4 opsi
        for distractor in distractors:
            if len(options) < 4 and distractor not in options:
                options.append(distractor)
        
        # Jika masih kurang, tambahkan opsi umum
        while len(options) < 4:
            generic_option = f"Opsi {len(options) + 1}"
            options.append(generic_option)
        
        random.shuffle(options)
        explanation = self.generate_explanation(q_type, concept, correct_answer, material_text)
        
        return options, correct_answer, explanation
    
    # Generate jawaban yang benar berdasarkan jenis soal
    def generate_correct_answer(self, q_type: str, concept: str, material_text: str) -> str:
        answers = {
            "definition": [
                f"{concept.capitalize()} adalah konsep penting yang dijelaskan dalam materi",
                f"Definisi {concept} tercantum secara detail dalam pembahasan",
                f"{concept.capitalize()} merujuk pada pengertian yang spesifik dalam konteks materi"
            ],
            "cause_effect": [
                f"{concept.capitalize()} dipengaruhi oleh berbagai faktor yang saling terkait",
                f"Dampak {concept} dapat dilihat dari beberapa aspek dalam materi",
                f"Penyebab {concept} dijelaskan melalui mekanisme tertentu"
            ],
            "comparison": [
                f"Perbandingan menunjukkan perbedaan karakteristik yang signifikan",
                f"Persamaan dan perbedaan dijelaskan melalui analisis komparatif",
                f"Kedua konsep memiliki keunikan dan karakteristik masing-masing"
            ],
            "application": [
                f"{concept.capitalize()} dapat diaplikasikan dalam berbagai situasi praktis",
                f"Penerapan {concept} membutuhkan pemahaman konsep yang mendalam",
                f"Aplikasi {concept} meliputi beberapa implementasi yang relevan"
            ],
            "simple": [
                f"{concept.capitalize()} adalah elemen fundamental dalam materi",
                f"Pemahaman {concept} penting untuk menguasai topik ini",
                f"{concept.capitalize()} memiliki peran kunci dalam pembahasan"
            ]
        }
        
        return random.choice(answers.get(q_type, answers["simple"]))
    
    # Generate distractor
    def generate_plausible_distractors(self, q_type: str, concept: str, concepts: List[str], material_text: str) -> List[str]:
        distractors = []
        general_distractors = [
            f"Konsep {concept} tidak relevan dengan materi",
            f"{concept.capitalize()} adalah istilah yang sudah usang",
            "Tidak ada penjelasan yang cukup dalam materi",
            "Jawaban tersebut tidak sesuai dengan konteks pembahasan"
        ]
        
        specific_distractors = {
            "definition": [
                f"{concept.capitalize()} memiliki pengertian yang berbeda dari penjelasan materi",
                f"Definisi {concept} tidak konsisten dengan pembahasan"
            ],
            "cause_effect": [
                f"{concept.capitalize()} tidak memiliki hubungan sebab-akibat yang jelas",
                "Hubungan kausalitas tidak terbukti dalam materi"
            ],
            "comparison": [
                "Perbandingan yang dilakukan tidak akurat",
                "Tidak ada perbedaan signifikan antara konsep-konsep tersebut"
            ]
        }
        
        distractors.extend(general_distractors)
        distractors.extend(specific_distractors.get(q_type, []))
        
        return random.sample(distractors, min(3, len(distractors)))
    
    # Generate penjelasan untuk jawaban yang benar
    def generate_explanation(self, q_type: str, concept: str, correct_answer: str, material_text: str) -> str:
        explanations = {
            "definition": f"Jawaban benar karena sesuai dengan definisi {concept} yang dijelaskan dalam materi.",
            "cause_effect": f"Jawaban benar karena mencerminkan hubungan sebab-akibat {concept} yang tepat.",
            "comparison": f"Jawaban benar karena menunjukkan perbandingan yang akurat berdasarkan materi.",
            "application": f"Jawaban benar karena sesuai dengan penerapan {concept} dalam konteks yang relevan.",
            "simple": f"Jawaban benar karena sesuai dengan penjelasan {concept} dalam materi pembelajaran."
        }
        return explanations.get(q_type, "Jawaban benar berdasarkan pembahasan dalam materi.")

# Class untuk mengelola dashboard
class DashboardManager:
    
    def __init__(self):
        self.analytics_data = {}
    
    # Buat data analytics untuk dashboard
    def create_analytics(self, questions: List[Question], results: List[Dict] = None):
        analytics = {
            "total_questions": len(questions),
            "difficulty_distribution": self.get_difficulty_distribution(questions),
            "question_types": self.get_question_types(questions),
            "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if results:
            analytics["quiz_results"] = self.analyze_quiz_results(results)
        
        return analytics
    
    # Dapatkan distribusi tingkat kesulitan
    def get_difficulty_distribution(self, questions: List[Question]) -> Dict:
        distribution = {"easy": 0, "medium": 0, "hard": 0}
        for q in questions:
            distribution[q.difficulty] += 1
        return distribution
    
    # Dapatkan distribusi jenis soal
    def get_question_types(self, questions: List[Question]) -> Dict:
        types_count = {}
        for q in questions:
            types_count[q.question_type] = types_count.get(q.question_type, 0) + 1
        return types_count
    
    # Analisis hasil kuis
    def analyze_quiz_results(self, results: List[Dict]) -> Dict:
        if not results:
            return {}
        
        correct_count = sum(1 for r in results if r['is_correct'])
        total_questions = len(results)
        accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        return {
            "correct_answers": correct_count,
            "total_questions": total_questions,
            "accuracy": accuracy,
            "performance": "Excellent" if accuracy >= 80 else "Good" if accuracy >= 60 else "Needs Improvement"
        }
    
    # Hitung rata-rata tingkat kesulitan
    def calculate_average_difficulty(self, diff_data: Dict) -> str:
        weights = {"easy": 1, "medium": 2, "hard": 3}
        total_weight = sum(diff_data.get(diff, 0) * weight for diff, weight in weights.items())
        total_questions = sum(diff_data.values())
        
        if total_questions == 0:
            return "N/A"
        
        avg = total_weight / total_questions
        if avg < 1.5:
            return "Mudah"
        elif avg < 2.5:
            return "Sedang"
        else:
            return "Sulit"

# Membuat link download untuk berbagai format
def create_download_link(data, filename, file_type):
    try:
        if file_type == "csv":
            if isinstance(data, list) and data:
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False, encoding='utf-8')
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">📥 Download CSV</a>'
                return href
        elif file_type == "json":
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            b64 = base64.b64encode(json_str.encode()).decode()
            href = f'<a href="data:application/json;base64,{b64}" download="{filename}.json">📥 Download JSON</a>'
            return href
        elif file_type == "txt":
            b64 = base64.b64encode(data.encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="{filename}.txt">📥 Download TXT</a>'
            return href
    except Exception as e:
        st.error(f"Error creating download link: {e}")
        return ""

# Main function untuk aplikasi
def main():
    st.set_page_config(
        page_title="AI Question Generator Pro",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS Style
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #4ECDC4;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        .correct-answer {
            background-color: #d4edda;
            padding: 0.2rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            border-left: 3px solid #28a745;
        }
        .incorrect-answer {
            background-color: #f8d7da;
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            border-left: 3px solid #dc3545;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header aplikasi dengan gradient effect
    st.markdown('<h1 class="main-header">🚀📚 AI Question Generator</h1>', unsafe_allow_html=True)
    st.markdown('<h2 align="center">📚 AI Question Generator dari Materi Ajar - Lengkap dengan Jawaban & Analytic</h2>', unsafe_allow_html=True)
    st.markdown("---")

    # Inisialisasi session state
    if 'material_processor' not in st.session_state:
        st.session_state.material_processor = MaterialProcessor()
    if 'question_generator' not in st.session_state:
        st.session_state.question_generator = AdvancedQuestionGenerator()
    if 'dashboard_manager' not in st.session_state:
        st.session_state.dashboard_manager = DashboardManager()
    if 'questions_generated' not in st.session_state:
        st.session_state.questions_generated = False
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = []
    if 'show_answers' not in st.session_state:
        st.session_state.show_answers = False
    if 'analytics_data' not in st.session_state:
        st.session_state.analytics_data = {}

    # Sidebar untuk upload file dan pengaturan
    with st.sidebar:
        st.header("📤 Upload Materi")
        uploaded_file = st.file_uploader(
            "Pilih file materi Anda",
            type=['pdf', 'docx', 'txt'],
            help="Upload file materi ajar dalam format PDF, DOCX, atau TXT"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

        st.header("⚙️ Pengaturan")
        num_questions = st.slider("Jumlah soal:", 5, 20, 10)
        include_explanations = st.checkbox("Sertakan penjelasan jawaban", value=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick stats di sidebar
        if st.session_state.questions_generated:
            st.markdown("---")
            st.subheader("📊 Quick Stats")
            st.metric("Total Soal", len(st.session_state.generated_questions))
            if st.session_state.analytics_data:
                diff_data = st.session_state.analytics_data.get("difficulty_distribution", {})
                st.write("**Distribusi Kesulitan:**")
                for diff, count in diff_data.items():
                    st.write(f"- {diff.capitalize()}: {count} soal")

    # Tab utama
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "🎯 Generate Soal", "📊 Analytics", "📥 Download"])
    
    with tab1:
        # Dashboard utama dengan metrics cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Status Generator", "Ready" if uploaded_file else "Waiting")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if st.session_state.questions_generated:
                st.metric("Soal Digenerate", len(st.session_state.generated_questions))
            else:
                st.metric("Soal Digenerate", "0")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            file_type = uploaded_file.type if uploaded_file else "None"
            st.metric("Format File", file_type.split('/')[-1].upper() if uploaded_file else "None")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.metric("AI Power", "Active")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Preview materi
        if uploaded_file:
            st.subheader("📖 Preview Materi")
            with st.spinner("Memproses materi..."):
                if st.session_state.material_processor.process_material(uploaded_file):
                    preview_text = st.session_state.material_processor.text_content[:300] + "..."
                    st.text_area("Preview Materi:", preview_text, height=150, key="preview_area")
                    
                    # Tampilkan key concepts
                    concepts = st.session_state.material_processor.get_key_concepts()
                    if concepts:
                        st.write("**Konsep Kunci yang Terdeteksi:**")
                        concepts_chips = " ".join([f"`{concept}`" for concept in concepts[:8]])
                        st.markdown(concepts_chips)
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 Generate Sekarang", type="primary", use_container_width=True):
                if uploaded_file:
                    with st.spinner("AI sedang generate soal..."):
                        questions = st.session_state.question_generator.generate_questions_advanced(
                            st.session_state.material_processor.text_content, 
                            num_questions
                        )
                        st.session_state.generated_questions = questions
                        st.session_state.questions_generated = True
                        st.session_state.analytics_data = st.session_state.dashboard_manager.create_analytics(questions)
                        st.success(f"✅ Berhasil generate {len(questions)} soal!")
                else:
                    st.warning("⚠️ Silakan upload materi terlebih dahulu")
        
        with col2:
            if st.session_state.questions_generated:
                if st.button("🔄 Generate Ulang", use_container_width=True):
                    st.session_state.questions_generated = False
                    st.session_state.generated_questions = []
                    st.rerun()
        
        with col3:
            if st.session_state.questions_generated:
                st.session_state.show_answers = st.checkbox("👀 Tampilkan Jawaban", value=True)
    
    with tab2:
        st.header("🎯 Soal yang Digenerate")
        if not st.session_state.questions_generated:
            st.info("👈 Upload materi dan klik 'Generate Sekarang' di tab Dashboard")
        else:
            # Toggle untuk tampilkan/sembunyikan jawaban
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Tampilan"):
                    st.rerun()
            
            # Tampilkan semua soal
            for i, question in enumerate(st.session_state.generated_questions):
                with st.container():
                    
                    # Header soal dengan metadata
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**Soal #{i+1}** - **{question.difficulty.upper()}**")
                    with col2:
                        st.caption(f"Type: {question.question_type}")
                    with col3:
                        st.caption(f"Options: {len(question.options)}")
                    
                    # Pertanyaan
                    st.markdown(f"**{question.question_text}**")
                    
                    # Opsi jawaban
                    for j, option in enumerate(question.options):
                        st.write(f"**{chr(65+j)}.** {option}")
                    
                    # Jawaban dan penjelasan jika ditampilkan
                    if st.session_state.show_answers:
                        correct_index = question.options.index(question.correct_answer) if question.correct_answer in question.options else 0
                        st.markdown(f'<div class="correct-answer">', unsafe_allow_html=True)
                        st.markdown(f"**✅ Jawaban Benar: {chr(65 + correct_index)}. {question.correct_answer}**")
                        if question.explanation:
                            st.markdown(f"**💡 Penjelasan:** {question.explanation}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("---")
    
    with tab3:
        st.header("📊 Analytics & Insights")
        if not st.session_state.questions_generated:
            st.info("👈 Generate soal terlebih dahulu untuk melihat analytics")
        else:
            # Visualisasi data
            col1, col2 = st.columns(2)
            with col1:
                # Pie chart untuk distribusi kesulitan
                diff_data = st.session_state.analytics_data.get("difficulty_distribution", {})
                if diff_data:
                    fig = px.pie(
                        values=list(diff_data.values()),
                        names=[d.upper() for d in diff_data.keys()],
                        title="📈 Distribusi Tingkat Kesulitan",
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Detailed statistics
            st.subheader("📋 Detail Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Soal", len(st.session_state.generated_questions))
                st.metric("Soal Mudah", diff_data.get("easy", 0))
            
            with col2:
                st.metric("Soal Sedang", diff_data.get("medium", 0))
                st.metric("Soal Sulit", diff_data.get("hard", 0))
            
            with col3:
                avg_difficulty = st.session_state.dashboard_manager.calculate_average_difficulty(diff_data)
                st.metric("Rata-rata Kesulitan", avg_difficulty)
                st.metric("Waktu Generate", st.session_state.analytics_data.get("generation_time", "N/A"))
    
    with tab4:
        st.header("📥 Download Soal")
        if not st.session_state.questions_generated:
            st.info("👈 Generate soal terlebih dahulu untuk mendownload")
        else:
            st.subheader("💾 Pilih Format Download")
            
            # Persiapan data untuk download
            questions_data = [q.to_dict() for q in st.session_state.generated_questions]
            
            # Format CSV
            csv_data = []
            for i, q in enumerate(questions_data):
                row = {
                    "No": i+1,
                    "Soal": q["question"],
                    "Jawaban_Benar": q["correct_answer"],
                    "Penjelasan": q.get("explanation", ""),
                    "Tipe": q["type"],
                    "Kesulitan": q["difficulty"]
                }
                # Tambahkan opsi
                for j, option in enumerate(q['options']):
                    row[f"Opsi_{chr(65+j)}"] = option
                csv_data.append(row)
            
            # Format Text
            text_content = "SOAL DAN JAWABAN\n================\n\n"
            for i, q in enumerate(questions_data):
                text_content += f"{i+1}. {q['question']}\n"
                for j, option in enumerate(q['options']):
                    text_content += f"   {chr(65+j)}. {option}\n"
                text_content += f"   ✅ Jawaban: {q['correct_answer']}\n"
                if q.get('explanation'):
                    text_content += f"   💡 Penjelasan: {q['explanation']}\n"
                text_content += "\n"
            
            # Tombol download
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(create_download_link(csv_data, "soal_dan_jawaban", "csv"), unsafe_allow_html=True)
            
            with col2:
                st.markdown(create_download_link(questions_data, "soal_dan_jawaban", "json"), unsafe_allow_html=True)
            
            with col3:
                st.markdown(create_download_link(text_content, "soal_dan_jawaban", "txt"), unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Preview data yang akan didownload
            st.subheader("👀 Preview Data")
            with st.expander("Lihat Preview"):
                if questions_data:
                    # Tampilkan preview 2 soal pertama
                    st.json(questions_data[:2])

if __name__ == "__main__":
    main()