#!/usr/bin/env python3
"""
Quick Database Setup for TotalEnergies Demo
Run this to populate the database with demo data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date
from app import create_app, db
from app.models.demo5_models import (
    TEProduct, TETechnicalDoc, TEFormulationTrial,
    TESAPInventory, TELIMSTest, TESupplier, TEGreetingResponse
)

def seed_all():
    app = create_app()
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("✓ Tables created\n")
        
        # Clear existing data
        print("Clearing existing TotalEnergies data...")
        TEProduct.query.delete()
        TETechnicalDoc.query.delete()
        TEFormulationTrial.query.delete()
        TESAPInventory.query.delete()
        TELIMSTest.query.delete()
        TESupplier.query.delete()
        TEGreetingResponse.query.delete()
        db.session.commit()
        print("✓ Cleared\n")
        
        # Products
        print("Seeding products...")
        products = [
            TEProduct(product_name="Quartz 9000 5W-30", product_code="QTZ-9000-5W30", product_type="lubricant", grade="Full Synthetic", specifications={'viscosity_100c': '11.2-11.8 cSt', 'api': 'SN Plus'}, market_segment="Premium Cars", status="active"),
            TEProduct(product_name="Quartz 7000 10W-40", product_code="QTZ-7000-10W40", product_type="lubricant", grade="Semi-Synthetic", specifications={'viscosity_100c': '14-15.5 cSt'}, market_segment="Mid-tier Cars", status="active"),
            TEProduct(product_name="TotalEnergies Domestic LPG", product_code="LPG-DOM-19KG", product_type="lpg", grade="Cooking Gas", specifications={'propane_min': '95%', 'moisture_max': '50 ppm'}, market_segment="Residential", status="active"),
        ]
        for p in products:
            db.session.add(p)
        db.session.commit()
        print(f"✓ Added {len(products)} products\n")
        
        # Technical Docs
        print("Seeding technical documents...")
        docs = [
            TETechnicalDoc(doc_type="formulation_spec", title="Quartz 9000 5W-30 Formulation Spec Rev 3.2", product_related="Quartz 9000 5W-30", content="PAO 4 cSt (30%), Group III 4 cSt (50%), VI Improver PMA (9%). Target viscosity 11.5 cSt @ 100°C. Recommended VI Improver dosage: 8.5-9.2% w/w PMA.", doc_metadata={'version': '3.2', 'author': 'Dr. Rajesh Kumar'}, tags="formulation,synthetic"),
            TETechnicalDoc(doc_type="test_protocol", title="PESO LPG Quality Control Protocol", product_related="Automotive LPG", content="Mandatory tests: Vapor pressure (ASTM D6897), Propane content (IS 4576), Moisture (BIS 14861). Test every batch. Automotive LPG requirements: Vapor pressure 6-8 bar @ 20°C, Propane content min 95%, Moisture max 50 ppm.", doc_metadata={'standard': 'PESO 2016'}, tags="lpg,quality_control"),
            TETechnicalDoc(doc_type="formulation_spec", title="Quartz 7000 10W-40 Technical Specification", product_related="Quartz 7000 10W-40", content="Semi-synthetic engine oil. Viscosity at 100°C: 14.2 cSt. Base: Group II (60%) + Group III (25%) + VI Improver (8%).", doc_metadata={'version': '2.1', 'author': 'Dr. Amit Sharma'}, tags="formulation,semi_synthetic"),
            TETechnicalDoc(doc_type="product_spec", title="LPG Moisture Content Specification", product_related="TotalEnergies Domestic LPG", content="Moisture content specification for LPG products: Maximum 50 ppm for domestic LPG, Maximum 30 ppm for automotive LPG. Test method: BIS 14861 Karl Fischer titration.", doc_metadata={'standard': 'BIS 14861'}, tags="lpg,moisture,specification"),
            TETechnicalDoc(doc_type="formulation_guide", title="Heavy-Duty Engine Oil Development Guide", product_related="Quartz 9000 HD", content="Heavy-duty variant requirements: Higher ZDDP content (1.8%), Enhanced dispersant package (12%), Extended drain intervals capability. Target: API CK-4, ACEA E9.", doc_metadata={'application': 'heavy_duty'}, tags="heavy_duty,commercial"),
        ]
        for d in docs:
            db.session.add(d)
        db.session.commit()
        print(f"✓ Added {len(docs)} technical documents\n")
        
        # Formulation Trials
        print("Seeding formulation trials...")
        trials = [
            TEFormulationTrial(trial_code="QTZ-9000-T2025-001", product_family="Quartz 9000", formulation={'base_oils': [{'type': 'PAO 4 cSt', 'pct': 30}, {'type': 'Group III 4 cSt', 'pct': 50}], 'additives': [{'type': 'ZDDP', 'pct': 1.2}, {'type': 'PMA VI Improver', 'pct': 9.0}]}, test_results={'viscosity_100c': 11.4, 'pass': True}, status="approved", engineer_name="Priya Sharma"),
            TEFormulationTrial(trial_code="HIPERF-T2025-005", product_family="Hi-Perf Moto", formulation={'base_oils': [{'type': 'Group II', 'pct': 70}]}, test_results={'jaso_ma2': 0.47}, status="testing", engineer_name="Amit Patel"),
            TEFormulationTrial(trial_code="QTZ-7000-T2025-003", product_family="Quartz 7000", formulation={'base_oils': [{'type': 'Group III', 'pct': 60}]}, test_results={}, status="testing", engineer_name="Ravi Kumar"),
            TEFormulationTrial(trial_code="LPG-T2025-008", product_family="LPG Domestic", formulation={'lpg_components': [{'type': 'Propane', 'pct': 96.5}]}, test_results={}, status="testing", engineer_name="Meera Singh"),
        ]
        for t in trials:
            db.session.add(t)
        db.session.commit()
        print(f"✓ Added {len(trials)} formulation trials\n")
        
        # SAP Inventory
        print("Seeding SAP inventory...")
        materials = [
            TESAPInventory(material_code="BASEOLL-GRP3-4CST", material_name="Group III Base Oil 4 cSt", material_category="base_oil", stock_quantity=45000, unit="L", price=95.50, supplier="Nayara Energy"),
            TESAPInventory(material_code="ADDPKG-ZDDP-SP", material_name="ZDDP Anti-wear Package", material_category="additive", stock_quantity=1200, unit="KG", price=450.00, supplier="Lubrizol India"),
            TESAPInventory(material_code="VIIMPR-PMA-9PCT", material_name="PMA VI Improver", material_category="additive", stock_quantity=3500, unit="KG", price=310.00, supplier="Evonik India"),
            # Low stock items for testing
            TESAPInventory(material_code="ADDPKG-DISP-8", material_name="Dispersant Package 8%", material_category="additive", stock_quantity=25, unit="KG", price=890.00, supplier="Lubrizol India"),
            TESAPInventory(material_code="BASEOLL-PAO-4", material_name="PAO 4 cSt Synthetic Base", material_category="base_oil", stock_quantity=150, unit="L", price=320.00, supplier="ExxonMobil"),
            TESAPInventory(material_code="ADDPKG-AW-BOOST", material_name="Anti-Wear Booster", material_category="additive", stock_quantity=8, unit="KG", price=1250.00, supplier="Afton Chemical"),
        ]
        for m in materials:
            db.session.add(m)
        db.session.commit()
        print(f"✓ Added {len(materials)} SAP inventory items\n")
        
        # LIMS Tests
        print("Seeding LIMS test results...")
        tests = [
            TELIMSTest(batch_code="QTZ-2025-0234", product_code="QTZ-9000-5W30", test_type="Engine Oil QC", test_date=date(2025, 3, 15), results={'viscosity_100c': 11.3, 'copper_ppm': 28}, pass_fail="FAIL", analyst="Sneha Reddy", notes="Copper contamination"),
            TELIMSTest(batch_code="LPG-DOM-2025-0312", product_code="LPG-DOM-19KG", test_type="LPG QC", test_date=date(2025, 3, 12), results={'moisture_ppm': 180, 'propane_pct': 96.2}, pass_fail="FAIL", analyst="Vikram Singh", notes="Moisture contamination"),
        ]
        for t in tests:
            db.session.add(t)
        db.session.commit()
        print(f"✓ Added {len(tests)} LIMS test results\n")
        
        # Suppliers
        print("Seeding suppliers...")
        suppliers = [
            TESupplier(supplier_name="Nayara Energy (Vadinar)", material_type="Group III Base Oil", location="Gujarat", lead_time_days=10, quality_rating=4.5, certifications=['ISO 9001', 'API Group III']),
            TESupplier(supplier_name="Lubrizol India", material_type="Additive Packages", location="Mumbai", lead_time_days=15, quality_rating=4.8, certifications=['ISO 9001', 'REACH']),
            TESupplier(supplier_name="Indian Oil Corporation", material_type="Group III Base Oil", location="Gujarat", lead_time_days=12, quality_rating=4.6, certifications=['ISO 9001', 'BIS']),
            TESupplier(supplier_name="Reliance Industries (Jamnagar)", material_type="Group III Base Oil", location="Gujarat", lead_time_days=8, quality_rating=4.7, certifications=['ISO 9001', 'API Group III', 'REACH']),
            TESupplier(supplier_name="Gujarat State Petronet Ltd", material_type="LPG", location="Gujarat", lead_time_days=5, quality_rating=4.4, certifications=['ISO 9001', 'PESO', 'BIS']),
            TESupplier(supplier_name="Evonik India", material_type="VI Improvers", location="Mumbai", lead_time_days=18, quality_rating=4.9, certifications=['ISO 9001', 'REACH', 'FDA']),
            TESupplier(supplier_name="Afton Chemical", material_type="Anti-wear Additives", location="Pune", lead_time_days=14, quality_rating=4.6, certifications=['ISO 9001', 'API']),
        ]
        for s in suppliers:
            db.session.add(s)
        db.session.commit()
        print(f"✓ Added {len(suppliers)} suppliers\n")
        
        # Greeting Responses
        print("Seeding greeting responses...")
        greetings = [
            # English greetings
            TEGreetingResponse(greeting_type="greeting", language="en", 
                             response_text="Hello! 👋 I'm your TotalEnergies Engineer's Copilot. I can help with formulation development, supply chain intelligence, quality control, technical documentation, and process optimization. I work in both English and Hindi. How can I assist you today?",
                             response_category="greeting", priority=1),
            TEGreetingResponse(greeting_type="greeting", language="en",
                             response_text="Hi there! I'm the Engineer's Copilot for TotalEnergies. I specialize in lubricant R&D, supplier management, inventory tracking, and technical analysis. What technical challenge can I help you solve?",
                             response_category="greeting", priority=2),
            TEGreetingResponse(greeting_type="capabilities", language="en",
                             response_text="🤖 **My Core Capabilities:**\n\n🔬 **Formulation Intelligence:** Lubricant recommendations, additive optimization, base oil selection\n🏭 **Supply Chain:** Real-time supplier info, inventory monitoring, procurement recommendations\n🧪 **Quality Control:** LIMS analysis, batch investigation, compliance validation\n📊 **Documentation:** Access to 1000+ technical documents and specifications\n🌐 **Multi-Language:** Full functionality in English and Hindi\n⚡ **Real-Time:** 2.3s average response time with source citations\n\nTry asking about specific products, suppliers, test results, or formulation challenges!",
                             response_category="capabilities", priority=1),
            
            # Hindi greetings  
            TEGreetingResponse(greeting_type="greeting", language="hi",
                             response_text="नमस्ते! 👋 मैं आपका TotalEnergies Engineer's Copilot हूं। मैं फॉर्मूलेशन विकास, आपूर्ति श्रृंखला बुद्धिमत्ता, गुणवत्ता नियंत्रण, तकनीकी दस्तावेज और प्रक्रिया अनुकूलन में सहायता कर सकता हूं। मैं अंग्रेजी और हिंदी दोनों में काम करता हूं। आज मैं आपकी कैसे सहायता कर सकता हूं?",
                             response_category="greeting", priority=1),
            TEGreetingResponse(greeting_type="greeting", language="hi",
                             response_text="हैलो! मैं TotalEnergies के लिए Engineer's Copilot हूं। मैं स्नेहक R&D, आपूर्तिकर्ता प्रबंधन, इन्वेंट्री ट्रैकिंग और तकनीकी विश्लेषण में विशेषज्ञ हूं। मैं आपकी किस तकनीकी चुनौती को हल करने में मदद कर सकता हूं?",
                             response_category="greeting", priority=2),
            TEGreetingResponse(greeting_type="capabilities", language="hi",
                             response_text="🤖 **मेरी मुख्य क्षमताएं:**\n\n🔬 **फॉर्मूलेशन बुद्धिमत्ता:** स्नेहक सिफारिशें, एडिटिव अनुकूलन, बेस ऑयल चयन\n🏭 **आपूर्ति श्रृंखला:** वास्तविक समय आपूर्तिकर्ता जानकारी, इन्वेंट्री निगरानी\n🧪 **गुणवत्ता नियंत्रण:** LIMS विश्लेषण, बैच जांच, अनुपालन सत्यापन\n📊 **दस्तावेज:** 1000+ तकनीकी दस्तावेजों तक पहुंच\n🌐 **बहु-भाषा:** अंग्रेजी और हिंदी में पूर्ण कार्यक्षमता\n⚡ **वास्तविक समय:** 2.3 सेकंड औसत प्रतिक्रिया समय\n\nविशिष्ट उत्पादों, आपूर्तिकर्ताओं, परीक्षण परिणामों या फॉर्मूलेशन चुनौतियों के बारे में पूछें!",
                             response_category="capabilities", priority=1),
        ]
        
        for g in greetings:
            db.session.add(g)
        db.session.commit()
        print(f"✓ Added {len(greetings)} greeting responses\n")
        
        print("=" * 60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 60)
        print("\nRun the app: python run.py")
        print("Then go to: http://localhost:5002/demo5/dashboard\n")

if __name__ == "__main__":
    seed_all()
