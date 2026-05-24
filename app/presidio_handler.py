# app/presidio_handler.py
import re
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from app.config import Config

class CustomPresidio:
    def __init__(self):
        print("🔧 Initializing Presidio...")
        try:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
            self._add_custom_recognizers()
            print("✅ Presidio ready")
        except Exception as e:
            print(f"⚠️ Presidio init error: {e}")
            self.analyzer = None
            self.anonymizer = None
    
    def _add_custom_recognizers(self):
        """Add custom recognizers for PII detection"""
        try:
            # Phone Number
            phone_patterns = [
                Pattern(name="phone_1", regex=r"03[0-9]{2}[- ]?[0-9]{7}", score=0.10),
                Pattern(name="phone_2", regex=r"03[0-9]{9}", score=0.10),
                Pattern(name="phone_3", regex=r"\+92[0-9]{10}", score=0.10),
            ]
            phone_recognizer = PatternRecognizer(
                supported_entity="PHONE_NUMBER",
                patterns=phone_patterns,
                context=["phone", "mobile", "contact", "call", "number"]
            )
            
            # API Key
            api_patterns = [
                Pattern(name="api_1", regex=r"sk-[a-zA-Z0-9]{48}", score=0.90),
                Pattern(name="api_2", regex=r"pk-[a-zA-Z0-9]{48}", score=0.90),
            ]
            api_recognizer = PatternRecognizer(
                supported_entity="API_KEY",
                patterns=api_patterns,
                context=["api", "key", "secret", "token", "openai"]
            )
            
            # Internal ID
            id_patterns = [
                Pattern(name="id_1", regex=r"STU-[0-9]{6}", score=0.80),
                Pattern(name="id_2", regex=r"HOG-[0-9]{6}", score=0.80),
                Pattern(name="id_3", regex=r"EMP-[0-9]{4}", score=0.80),
            ]
            id_recognizer = PatternRecognizer(
                supported_entity="INTERNAL_ID",
                patterns=id_patterns,
                context=["student", "id", "employee", "registration", "hogwarts"]
            )
            
            # Email
            email_patterns = [
                Pattern(name="email", regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", score=0.95),
            ]
            email_recognizer = PatternRecognizer(
                supported_entity="EMAIL",
                patterns=email_patterns,
                context=["email", "mail", "address"]
            )
            
            if self.analyzer:
                self.analyzer.registry.add_recognizer(phone_recognizer)
                self.analyzer.registry.add_recognizer(api_recognizer)
                self.analyzer.registry.add_recognizer(id_recognizer)
                self.analyzer.registry.add_recognizer(email_recognizer)
                print("✅ Added custom recognizers")
        except Exception as e:
            print(f"⚠️ Error adding recognizers: {e}")
    
    def analyze(self, text: str):
        """Analyze text for PII"""
        if not self.analyzer:
            return []
        
        try:
            results = self.analyzer.analyze(text=text, language="en")
            if results:
                print(f"🔍 Presidio found: {len(results)} entities")
                for r in results:
                    print(f"     - {r.entity_type}: '{text[r.start:r.end]}'")
            return results
        except Exception as e:
            print(f"⚠️ Presidio analyze error: {e}")
            return []
    
    def anonymize(self, text: str, results):
        """Anonymize detected PII"""
        if not self.anonymizer or not results:
            class SimpleResult:
                def __init__(self, text):
                    self.text = text
            return SimpleResult(text)
        
        try:
            operators = {
                "PHONE_NUMBER": OperatorConfig("mask", {"chars_to_mask": "*"}),
                "API_KEY": OperatorConfig("mask", {"chars_to_mask": "*"}),
                "INTERNAL_ID": OperatorConfig("mask", {"chars_to_mask": "*"}),
                "EMAIL": OperatorConfig("mask", {"chars_to_mask": "*"}),
                "PERSON": OperatorConfig("mask", {"chars_to_mask": "*"}),
            }
            return self.anonymizer.anonymize(text=text, analyzer_results=results, operators=operators)
        except Exception as e:
            print(f"⚠️ Anonymize error: {e}")
            class SimpleResult:
                def __init__(self, text):
                    self.text = text
            return SimpleResult(text)