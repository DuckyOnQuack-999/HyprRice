"""
Tests for the AI Workflow system

This module tests the AI-powered component enhancement pipeline,
including research, analysis, integration, and testing phases.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.hyprrice.ai_workflow import (
    AIWorkflowEngine, ResearchData, ComponentAnalysis, WorkflowResult,
    AIWorkflowWorker
)
from src.hyprrice.config import Config
from src.hyprrice.exceptions import HyprRiceError


class TestResearchData:
    """Test ResearchData dataclass"""
    
    def test_research_data_creation(self):
        """Test creating ResearchData instance"""
        research = ResearchData(
            web_resources=[{"url": "test.com", "title": "Test"}],
            known_issues=[{"issue_id": "BUG-001", "description": "Test bug"}],
            examples=[{"source": "GitHub", "url": "github.com/test"}],
            best_practices=["Use proper error handling"],
            performance_tips=["Optimize memory usage"],
            security_considerations=["Validate inputs"]
        )
        
        assert len(research.web_resources) == 1
        assert len(research.known_issues) == 1
        assert len(research.examples) == 1
        assert len(research.best_practices) == 1
        assert len(research.performance_tips) == 1
        assert len(research.security_considerations) == 1


class TestComponentAnalysis:
    """Test ComponentAnalysis dataclass"""
    
    def test_component_analysis_creation(self):
        """Test creating ComponentAnalysis instance"""
        analysis = ComponentAnalysis(
            logic_map={"classes": [], "functions": []},
            missing_logic=["Add error handling"],
            improvements=["Refactor complex function"],
            possible_features=["Add logging"],
            performance_issues=["Memory leak"],
            security_concerns=["Input validation"],
            code_quality_score=0.8
        )
        
        assert analysis.code_quality_score == 0.8
        assert len(analysis.missing_logic) == 1
        assert len(analysis.improvements) == 1
        assert len(analysis.possible_features) == 1


class TestWorkflowResult:
    """Test WorkflowResult dataclass"""
    
    def test_workflow_result_creation(self):
        """Test creating WorkflowResult instance"""
        result = WorkflowResult(
            success=True,
            component_path="/test/component.py",
            changes_applied=["Added error handling"],
            tests_passed=True,
            performance_improvement=0.15,
            error_log=[],
            execution_time=5.2
        )
        
        assert result.success is True
        assert result.tests_passed is True
        assert result.performance_improvement == 0.15
        assert result.execution_time == 5.2


class TestAIWorkflowEngine:
    """Test AIWorkflowEngine class"""
    
    @pytest.fixture
    def config(self):
        """Create test config"""
        return Config()
    
    @pytest.fixture
    def workflow_engine(self, config):
        """Create AIWorkflowEngine instance"""
        return AIWorkflowEngine(config)
    
    @pytest.fixture
    def temp_component_file(self):
        """Create temporary component file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
class TestComponent:
    def __init__(self):
        self.value = 0
    
    def get_value(self):
        return self.value
    
    def set_value(self, value):
        self.value = value
""")
            return f.name
    
    def test_workflow_engine_initialization(self, config):
        """Test AIWorkflowEngine initialization"""
        engine = AIWorkflowEngine(config)
        assert engine.config == config
        assert engine.research_cache == {}
        assert engine.analysis_cache == {}
    
    def test_setup_environment_success(self, workflow_engine, temp_component_file):
        """Test successful environment setup"""
        with patch.object(workflow_engine.backup_manager, 'create_backup') as mock_backup:
            mock_backup.return_value = "/backup/path"
            
            result = workflow_engine.setup_environment(temp_component_file)
            
            assert result is True
            mock_backup.assert_called_once_with(temp_component_file)
    
    def test_setup_environment_failure(self, workflow_engine):
        """Test environment setup failure"""
        with patch.object(workflow_engine, '_install_dependencies', side_effect=Exception("Install failed")):
            result = workflow_engine.setup_environment("/nonexistent/file.py")
            assert result is False
    
    def test_research_component(self, workflow_engine):
        """Test component research"""
        with patch.object(workflow_engine, '_fetch_web_resources') as mock_web, \
             patch.object(workflow_engine, '_fetch_known_issues') as mock_issues, \
             patch.object(workflow_engine, '_fetch_example_implementations') as mock_examples, \
             patch.object(workflow_engine, '_analyze_best_practices') as mock_practices, \
             patch.object(workflow_engine, '_get_performance_tips') as mock_perf, \
             patch.object(workflow_engine, '_get_security_considerations') as mock_sec:
            
            mock_web.return_value = [{"url": "test.com", "title": "Test"}]
            mock_issues.return_value = [{"issue_id": "BUG-001", "description": "Test"}]
            mock_examples.return_value = [{"source": "GitHub", "url": "github.com"}]
            mock_practices.return_value = ["Best practice 1"]
            mock_perf.return_value = ["Performance tip 1"]
            mock_sec.return_value = ["Security consideration 1"]
            
            research = workflow_engine.research_component("TestComponent")
            
            assert isinstance(research, ResearchData)
            assert len(research.web_resources) == 1
            assert len(research.known_issues) == 1
            assert len(research.examples) == 1
            assert len(research.best_practices) == 1
            assert len(research.performance_tips) == 1
            assert len(research.security_considerations) == 1
    
    def test_research_component_caching(self, workflow_engine):
        """Test research component caching"""
        with patch.object(workflow_engine, '_fetch_web_resources') as mock_web:
            mock_web.return_value = []
            
            # First call
            research1 = workflow_engine.research_component("TestComponent")
            
            # Second call should use cache
            research2 = workflow_engine.research_component("TestComponent")
            
            # Should only call fetch once
            assert mock_web.call_count == 1
            assert research1 == research2
    
    def test_analyze_component(self, workflow_engine, temp_component_file):
        """Test component analysis"""
        research = ResearchData([], [], [], [], [], [])
        
        with patch.object(workflow_engine, '_map_component_logic') as mock_map, \
             patch.object(workflow_engine, '_identify_missing_logic') as mock_missing, \
             patch.object(workflow_engine, '_identify_improvement_areas') as mock_improve, \
             patch.object(workflow_engine, '_suggest_new_features') as mock_features, \
             patch.object(workflow_engine, '_analyze_performance_issues') as mock_perf, \
             patch.object(workflow_engine, '_analyze_security_concerns') as mock_sec, \
             patch.object(workflow_engine, '_calculate_code_quality_score') as mock_quality:
            
            mock_map.return_value = {"classes": [], "functions": []}
            mock_missing.return_value = ["Missing logic 1"]
            mock_improve.return_value = ["Improvement 1"]
            mock_features.return_value = ["Feature 1"]
            mock_perf.return_value = ["Performance issue 1"]
            mock_sec.return_value = ["Security concern 1"]
            mock_quality.return_value = 0.8
            
            analysis = workflow_engine.analyze_component(temp_component_file, research)
            
            assert isinstance(analysis, ComponentAnalysis)
            assert analysis.code_quality_score == 0.8
            assert len(analysis.missing_logic) == 1
            assert len(analysis.improvements) == 1
            assert len(analysis.possible_features) == 1
    
    def test_prepare_inputs_success(self, workflow_engine):
        """Test successful input preparation"""
        result = workflow_engine.prepare_inputs("Test prompt", "test.py")
        assert "prompt=Test+prompt" in result
    
    def test_prepare_inputs_invalid_file_type(self, workflow_engine):
        """Test input preparation with invalid file type"""
        with pytest.raises(ValueError, match="Unsupported file type"):
            workflow_engine.prepare_inputs("Test prompt", "test.xyz")
    
    def test_prepare_inputs_empty_prompt(self, workflow_engine):
        """Test input preparation with empty prompt"""
        with pytest.raises(ValueError, match="Invalid inputs provided"):
            workflow_engine.prepare_inputs("", "test.py")
    
    def test_integrate_updates(self, workflow_engine, temp_component_file):
        """Test update integration"""
        analysis = ComponentAnalysis(
            logic_map={},
            missing_logic=["Add error handling"],
            improvements=["Refactor function"],
            possible_features=["Add logging"],
            performance_issues=[],
            security_concerns=[],
            code_quality_score=0.5
        )
        
        result_path = workflow_engine.integrate_updates(temp_component_file, analysis)
        
        assert result_path == temp_component_file
        
        # Check that file was modified
        with open(temp_component_file, 'r') as f:
            content = f.read()
            assert "AI Workflow Additions:" in content
            assert "Add error handling" in content
    
    def test_design_gui(self, workflow_engine, temp_component_file):
        """Test GUI design"""
        gui_layout = workflow_engine.design_gui(temp_component_file)
        
        assert isinstance(gui_layout, dict)
        assert "type" in gui_layout
        assert "elements" in gui_layout
        assert "layout" in gui_layout
    
    def test_design_gui_with_reference_image(self, workflow_engine, temp_component_file):
        """Test GUI design with reference image"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img_file:
            img_file.write(b"fake image data")
            img_path = img_file.name
        
        try:
            gui_layout = workflow_engine.design_gui(temp_component_file, img_path)
            
            assert isinstance(gui_layout, dict)
            # Should include reference image in elements
            elements = gui_layout.get("elements", [])
            image_elements = [e for e in elements if e.get("type") == "image"]
            assert len(image_elements) > 0
        finally:
            os.unlink(img_path)
    
    def test_execute_and_test_success(self, workflow_engine, temp_component_file):
        """Test successful execution and testing"""
        gui_layout = {"type": "test", "elements": []}
        
        with patch.object(workflow_engine, '_run_component') as mock_run, \
             patch.object(workflow_engine, '_test_component') as mock_test:
            
            mock_run.return_value = {"status": "success", "output": "Success"}
            mock_test.return_value = {
                "passed": True,
                "errors": [],
                "changes": ["Test change"],
                "performance_improvement": 0.1
            }
            
            result = workflow_engine.execute_and_test(temp_component_file, gui_layout)
            
            assert isinstance(result, WorkflowResult)
            assert result.success is True
            assert result.tests_passed is True
            assert result.performance_improvement == 0.1
    
    def test_execute_and_test_failure(self, workflow_engine, temp_component_file):
        """Test execution and testing failure"""
        gui_layout = {"type": "test", "elements": []}
        
        with patch.object(workflow_engine, '_run_component') as mock_run, \
             patch.object(workflow_engine, '_test_component') as mock_test:
            
            mock_run.return_value = {"status": "error", "output": "Test error"}
            mock_test.return_value = {
                "passed": False,
                "errors": ["Test error"],
                "changes": [],
                "performance_improvement": 0.0
            }
            
            result = workflow_engine.execute_and_test(temp_component_file, gui_layout)
            
            assert isinstance(result, WorkflowResult)
            assert result.success is False
            assert result.tests_passed is False
            assert len(result.error_log) > 0
    
    def test_review_and_deliver_success(self, workflow_engine, temp_component_file):
        """Test successful review and delivery"""
        result = WorkflowResult(
            success=True,
            component_path=temp_component_file,
            changes_applied=["Test change"],
            tests_passed=True,
            performance_improvement=0.1,
            error_log=[],
            execution_time=1.0
        )
        
        with patch.object(workflow_engine, '_verify_integration') as mock_verify, \
             patch.object(workflow_engine, '_document_changes') as mock_doc, \
             patch.object(workflow_engine, '_deliver_component') as mock_deliver:
            
            mock_verify.return_value = True
            
            success = workflow_engine.review_and_deliver(temp_component_file, result)
            
            assert success is True
            mock_verify.assert_called_once()
            mock_doc.assert_called_once()
            mock_deliver.assert_called_once()
    
    def test_review_and_deliver_verification_failure(self, workflow_engine, temp_component_file):
        """Test review and delivery with verification failure"""
        result = WorkflowResult(
            success=True,
            component_path=temp_component_file,
            changes_applied=["Test change"],
            tests_passed=True,
            performance_improvement=0.1,
            error_log=[],
            execution_time=1.0
        )
        
        with patch.object(workflow_engine, '_verify_integration') as mock_verify:
            mock_verify.return_value = False
            
            success = workflow_engine.review_and_deliver(temp_component_file, result)
            
            assert success is False
    
    def test_ai_component_pipeline_success(self, workflow_engine, temp_component_file):
        """Test successful AI component pipeline"""
        with patch.object(workflow_engine, 'setup_environment') as mock_setup, \
             patch.object(workflow_engine, 'research_component') as mock_research, \
             patch.object(workflow_engine, 'analyze_component') as mock_analyze, \
             patch.object(workflow_engine, 'prepare_inputs') as mock_prepare, \
             patch.object(workflow_engine, 'integrate_updates') as mock_integrate, \
             patch.object(workflow_engine, 'design_gui') as mock_design, \
             patch.object(workflow_engine, 'execute_and_test') as mock_execute, \
             patch.object(workflow_engine, 'review_and_deliver') as mock_review:
            
            mock_setup.return_value = True
            mock_research.return_value = ResearchData([], [], [], [], [], [])
            mock_analyze.return_value = ComponentAnalysis({}, [], [], [], [], [], 0.5)
            mock_prepare.return_value = "encoded_prompt"
            mock_integrate.return_value = temp_component_file
            mock_design.return_value = {"type": "test"}
            mock_execute.return_value = WorkflowResult(
                success=True, component_path=temp_component_file,
                changes_applied=[], tests_passed=True, performance_improvement=0.1,
                error_log=[], execution_time=1.0
            )
            mock_review.return_value = True
            
            result = workflow_engine.ai_component_pipeline(
                temp_component_file, "TestComponent", "Test prompt"
            )
            
            assert isinstance(result, WorkflowResult)
            assert result.success is True
    
    def test_ai_component_pipeline_setup_failure(self, workflow_engine, temp_component_file):
        """Test AI component pipeline with setup failure"""
        with patch.object(workflow_engine, 'setup_environment') as mock_setup:
            mock_setup.return_value = False
            
            result = workflow_engine.ai_component_pipeline(
                temp_component_file, "TestComponent", "Test prompt"
            )
            
            assert isinstance(result, WorkflowResult)
            assert result.success is False
    
    def test_ai_component_pipeline_exception(self, workflow_engine, temp_component_file):
        """Test AI component pipeline with exception"""
        with patch.object(workflow_engine, 'setup_environment', side_effect=Exception("Test error")):
            result = workflow_engine.ai_component_pipeline(
                temp_component_file, "TestComponent", "Test prompt"
            )
            
            assert isinstance(result, WorkflowResult)
            assert result.success is False
            assert len(result.error_log) > 0
    
    def test_confirm_file_type(self, workflow_engine):
        """Test file type confirmation"""
        assert workflow_engine._confirm_file_type("test.py") is True
        assert workflow_engine._confirm_file_type("test.js") is True
        assert workflow_engine._confirm_file_type("test.ts") is True
        assert workflow_engine._confirm_file_type("test.cpp") is True
        assert workflow_engine._confirm_file_type("test.md") is True
        assert workflow_engine._confirm_file_type("test.json") is True
        assert workflow_engine._confirm_file_type("test.yaml") is True
        assert workflow_engine._confirm_file_type("test.xyz") is False
    
    def test_get_file_type(self, workflow_engine):
        """Test file type extraction"""
        assert workflow_engine._get_file_type("/path/to/test.py") == ".py"
        assert workflow_engine._get_file_type("/path/to/test.js") == ".js"
        assert workflow_engine._get_file_type("test.ts") == ".ts"
    
    def test_calculate_code_quality_score(self, workflow_engine, temp_component_file):
        """Test code quality score calculation"""
        score = workflow_engine._calculate_code_quality_score(temp_component_file)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_calculate_code_quality_score_nonexistent_file(self, workflow_engine):
        """Test code quality score for nonexistent file"""
        score = workflow_engine._calculate_code_quality_score("/nonexistent/file.py")
        assert score == 0.0
    
    def test_apply_missing_logic(self, workflow_engine):
        """Test applying missing logic"""
        content = "class Test:\n    pass"
        missing_logic = ["Add error handling", "Add logging"]
        
        result = workflow_engine._apply_missing_logic(content, missing_logic)
        
        assert "AI Workflow Additions:" in result
        assert "Add error handling" in result
        assert "Add logging" in result
    
    def test_apply_improvements(self, workflow_engine):
        """Test applying improvements"""
        content = "class Test:\n    pass"
        improvements = ["Refactor function", "Optimize performance"]
        
        result = workflow_engine._apply_improvements(content, improvements)
        
        assert "AI Workflow Improvements:" in result
        assert "Refactor function" in result
        assert "Optimize performance" in result
    
    def test_add_features(self, workflow_engine):
        """Test adding features"""
        content = "class Test:\n    pass"
        features = ["Add configuration", "Add plugin system"]
        
        result = workflow_engine._add_features(content, features)
        
        assert "AI Workflow Features:" in result
        assert "Add configuration" in result
        assert "Add plugin system" in result
    
    def test_create_gui_layout(self, workflow_engine, temp_component_file):
        """Test GUI layout creation"""
        layout = workflow_engine._create_gui_layout(temp_component_file)
        
        assert isinstance(layout, dict)
        assert "type" in layout
        assert "elements" in layout
        assert "layout" in layout
        assert "styling" in layout
    
    def test_include_all_elements(self, workflow_engine):
        """Test including all GUI elements"""
        layout = {"elements": []}
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img_file:
            img_file.write(b"fake image data")
            img_path = img_file.name
        
        try:
            result = workflow_engine._include_all_elements(layout, img_path)
            
            assert "elements" in result
            elements = result["elements"]
            image_elements = [e for e in elements if e.get("type") == "image"]
            assert len(image_elements) > 0
        finally:
            os.unlink(img_path)
    
    def test_enhance_gui(self, workflow_engine):
        """Test GUI enhancement"""
        layout = {"elements": []}
        
        result = workflow_engine._enhance_gui(layout)
        
        assert "enhancements" in result
        enhancements = result["enhancements"]
        assert "animations" in enhancements
        assert "accessibility" in enhancements
        assert "responsive" in enhancements
        assert "tooltips" in enhancements
    
    def test_integrate_gui(self, workflow_engine, temp_component_file):
        """Test GUI integration"""
        gui_layout = {"type": "test", "elements": []}
        
        # Should not raise exception
        workflow_engine._integrate_gui(temp_component_file, gui_layout)
    
    def test_run_component_success(self, workflow_engine, temp_component_file):
        """Test successful component execution"""
        result = workflow_engine._run_component(temp_component_file)
        
        assert isinstance(result, dict)
        assert "status" in result
        assert "output" in result
        assert "performance_metrics" in result
    
    def test_test_component_success(self, workflow_engine):
        """Test component testing with success"""
        run_output = {"status": "success", "output": "Success"}
        
        result = workflow_engine._test_component(run_output)
        
        assert isinstance(result, dict)
        assert result["passed"] is True
        assert len(result["errors"]) == 0
    
    def test_test_component_failure(self, workflow_engine):
        """Test component testing with failure"""
        run_output = {"status": "error", "output": "Test error"}
        
        result = workflow_engine._test_component(run_output)
        
        assert isinstance(result, dict)
        assert result["passed"] is False
        assert len(result["errors"]) > 0
    
    def test_refine_component(self, workflow_engine, temp_component_file):
        """Test component refinement"""
        errors = ["Test error 1", "Test error 2"]
        
        # Should not raise exception
        workflow_engine._refine_component(temp_component_file, errors)
    
    def test_verify_integration(self, workflow_engine, temp_component_file):
        """Test integration verification"""
        result = WorkflowResult(
            success=True, component_path=temp_component_file,
            changes_applied=[], tests_passed=True, performance_improvement=0.1,
            error_log=[], execution_time=1.0
        )
        
        verification_result = workflow_engine._verify_integration(temp_component_file, result)
        
        assert isinstance(verification_result, bool)
    
    def test_document_changes(self, workflow_engine, temp_component_file):
        """Test change documentation"""
        result = WorkflowResult(
            success=True, component_path=temp_component_file,
            changes_applied=["Test change"], tests_passed=True, performance_improvement=0.1,
            error_log=[], execution_time=1.0
        )
        
        # Should not raise exception
        workflow_engine._document_changes(temp_component_file, result)
        
        # Check that documentation file was created
        doc_path = f"{temp_component_file}.ai_workflow.md"
        assert os.path.exists(doc_path)
        
        # Clean up
        if os.path.exists(doc_path):
            os.unlink(doc_path)
    
    def test_deliver_component(self, workflow_engine, temp_component_file):
        """Test component delivery"""
        # Should not raise exception
        workflow_engine._deliver_component(temp_component_file)
    
    def test_install_dependencies(self, workflow_engine):
        """Test dependency installation"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            # Should not raise exception
            workflow_engine._install_dependencies()
    
    def test_verify_environment(self, workflow_engine):
        """Test environment verification"""
        with patch('sys.version_info', (3, 8, 0)):
            # Should not raise exception
            workflow_engine._verify_environment()
    
    def test_verify_environment_old_python(self, workflow_engine):
        """Test environment verification with old Python version"""
        with patch('sys.version_info', (3, 7, 0)):
            with pytest.raises(ValueError, match="Python 3.8\\+ required"):
                workflow_engine._verify_environment()
    
    def test_verify_environment_missing_package(self, workflow_engine):
        """Test environment verification with missing package"""
        with patch('sys.version_info', (3, 8, 0)):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'PyQt6'")):
                with pytest.raises(ValueError, match="Required package PyQt6 not installed"):
                    workflow_engine._verify_environment()
    
    def test_fetch_web_resources(self, workflow_engine):
        """Test web resource fetching"""
        resources = workflow_engine._fetch_web_resources("TestComponent")
        
        assert isinstance(resources, list)
        assert len(resources) > 0
        assert "url" in resources[0]
        assert "title" in resources[0]
    
    def test_fetch_known_issues(self, workflow_engine):
        """Test known issues fetching"""
        issues = workflow_engine._fetch_known_issues("TestComponent")
        
        assert isinstance(issues, list)
        assert len(issues) > 0
        assert "issue_id" in issues[0]
        assert "description" in issues[0]
    
    def test_fetch_example_implementations(self, workflow_engine):
        """Test example implementations fetching"""
        examples = workflow_engine._fetch_example_implementations("TestComponent")
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        assert "source" in examples[0]
        assert "url" in examples[0]
    
    def test_analyze_best_practices(self, workflow_engine):
        """Test best practices analysis"""
        practices = workflow_engine._analyze_best_practices("TestComponent")
        
        assert isinstance(practices, list)
        assert len(practices) > 0
        assert all(isinstance(p, str) for p in practices)
    
    def test_get_performance_tips(self, workflow_engine):
        """Test performance tips retrieval"""
        tips = workflow_engine._get_performance_tips("TestComponent")
        
        assert isinstance(tips, list)
        assert len(tips) > 0
        assert all(isinstance(t, str) for t in tips)
    
    def test_get_security_considerations(self, workflow_engine):
        """Test security considerations retrieval"""
        considerations = workflow_engine._get_security_considerations("TestComponent")
        
        assert isinstance(considerations, list)
        assert len(considerations) > 0
        assert all(isinstance(c, str) for c in considerations)
    
    def test_map_component_logic(self, workflow_engine, temp_component_file):
        """Test component logic mapping"""
        logic_map = workflow_engine._map_component_logic(temp_component_file)
        
        assert isinstance(logic_map, dict)
        assert "classes" in logic_map
        assert "functions" in logic_map
        assert "imports" in logic_map
        assert "variables" in logic_map
        assert "complexity_score" in logic_map
    
    def test_map_component_logic_invalid_file(self, workflow_engine):
        """Test component logic mapping with invalid file"""
        logic_map = workflow_engine._map_component_logic("/nonexistent/file.py")
        
        assert isinstance(logic_map, dict)
        assert logic_map == {}
    
    def test_identify_missing_logic(self, workflow_engine):
        """Test missing logic identification"""
        logic_map = {
            "functions": [
                {"name": "test_function", "args": [], "complexity": 10}
            ]
        }
        research = ResearchData([], [], [], [], [], [])
        
        missing = workflow_engine._identify_missing_logic(logic_map, research)
        
        assert isinstance(missing, list)
        assert len(missing) > 0
        assert all(isinstance(m, str) for m in missing)
    
    def test_identify_improvement_areas(self, workflow_engine):
        """Test improvement areas identification"""
        logic_map = {
            "functions": [
                {"name": "complex_function", "args": [], "complexity": 100}
            ]
        }
        research = ResearchData([], [], [], ["Best practice"], [], [])
        
        improvements = workflow_engine._identify_improvement_areas(logic_map, research)
        
        assert isinstance(improvements, list)
        assert len(improvements) > 0
        assert all(isinstance(i, str) for i in improvements)
    
    def test_suggest_new_features(self, workflow_engine):
        """Test new feature suggestions"""
        research = ResearchData([], [], [], [], [], [])
        
        features = workflow_engine._suggest_new_features(research)
        
        assert isinstance(features, list)
        assert len(features) > 0
        assert all(isinstance(f, str) for f in features)
    
    def test_analyze_performance_issues(self, workflow_engine, temp_component_file):
        """Test performance issues analysis"""
        issues = workflow_engine._analyze_performance_issues(temp_component_file)
        
        assert isinstance(issues, list)
        assert len(issues) > 0
        assert all(isinstance(i, str) for i in issues)
    
    def test_analyze_security_concerns(self, workflow_engine, temp_component_file):
        """Test security concerns analysis"""
        concerns = workflow_engine._analyze_security_concerns(temp_component_file)
        
        assert isinstance(concerns, list)
        assert len(concerns) > 0
        assert all(isinstance(c, str) for c in concerns)
    
    def test_validate_inputs(self, workflow_engine):
        """Test input validation"""
        assert workflow_engine._validate_inputs("Test prompt", "test.py") is True
        assert workflow_engine._validate_inputs("", "test.py") is False
        assert workflow_engine._validate_inputs("Test prompt", "test.xyz") is False


class TestAIWorkflowWorker:
    """Test AIWorkflowWorker class"""
    
    @pytest.fixture
    def config(self):
        """Create test config"""
        return Config()
    
    @pytest.fixture
    def workflow_engine(self, config):
        """Create AIWorkflowEngine instance"""
        return AIWorkflowEngine(config)
    
    @pytest.fixture
    def temp_component_file(self):
        """Create temporary component file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("class TestComponent:\n    pass")
            return f.name
    
    def test_worker_initialization(self, workflow_engine, temp_component_file):
        """Test AIWorkflowWorker initialization"""
        worker = AIWorkflowWorker(
            workflow_engine, temp_component_file, "TestComponent", "Test prompt"
        )
        
        assert worker.workflow_engine == workflow_engine
        assert worker.component_path == temp_component_file
        assert worker.component_name == "TestComponent"
        assert worker.prompt == "Test prompt"
        assert worker.reference_image is None
    
    def test_worker_with_reference_image(self, workflow_engine, temp_component_file):
        """Test AIWorkflowWorker with reference image"""
        worker = AIWorkflowWorker(
            workflow_engine, temp_component_file, "TestComponent", "Test prompt", "/path/to/image.png"
        )
        
        assert worker.reference_image == "/path/to/image.png"
    
    def test_worker_run_success(self, workflow_engine, temp_component_file):
        """Test successful worker execution"""
        with patch.object(workflow_engine, 'ai_component_pipeline') as mock_pipeline:
            mock_result = WorkflowResult(
                success=True, component_path=temp_component_file,
                changes_applied=[], tests_passed=True, performance_improvement=0.1,
                error_log=[], execution_time=1.0
            )
            mock_pipeline.return_value = mock_result
            
            worker = AIWorkflowWorker(
                workflow_engine, temp_component_file, "TestComponent", "Test prompt"
            )
            
            # Mock signals
            worker.progress = Mock()
            worker.finished = Mock()
            worker.error = Mock()
            
            worker.run()
            
            mock_pipeline.assert_called_once_with(
                temp_component_file, "TestComponent", "Test prompt", None
            )
            worker.finished.emit.assert_called_once_with(mock_result)
    
    def test_worker_run_exception(self, workflow_engine, temp_component_file):
        """Test worker execution with exception"""
        with patch.object(workflow_engine, 'ai_component_pipeline', side_effect=Exception("Test error")):
            worker = AIWorkflowWorker(
                workflow_engine, temp_component_file, "TestComponent", "Test prompt"
            )
            
            # Mock signals
            worker.progress = Mock()
            worker.finished = Mock()
            worker.error = Mock()
            
            worker.run()
            
            worker.error.emit.assert_called_once_with("Test error")


# Integration tests
class TestAIWorkflowIntegration:
    """Integration tests for AI Workflow system"""
    
    @pytest.fixture
    def config(self):
        """Create test config"""
        return Config()
    
    @pytest.fixture
    def temp_component_file(self):
        """Create temporary component file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
class TestComponent:
    def __init__(self):
        self.value = 0
    
    def get_value(self):
        return self.value
    
    def set_value(self, value):
        self.value = value
""")
            return f.name
    
    def test_full_workflow_integration(self, config, temp_component_file):
        """Test full workflow integration"""
        workflow_engine = AIWorkflowEngine(config)
        
        # Mock external dependencies
        with patch.object(workflow_engine.backup_manager, 'create_backup') as mock_backup, \
             patch('subprocess.run') as mock_subprocess:
            
            mock_backup.return_value = "/backup/path"
            mock_subprocess.return_value = Mock(returncode=0)
            
            result = workflow_engine.ai_component_pipeline(
                temp_component_file, "TestComponent", "Add error handling and logging"
            )
            
            assert isinstance(result, WorkflowResult)
            # The result might be successful or not depending on the mocked components
            assert result.component_path == temp_component_file
    
    def test_workflow_with_real_file_operations(self, config, temp_component_file):
        """Test workflow with real file operations"""
        workflow_engine = AIWorkflowEngine(config)
        
        # Mock only external dependencies, allow real file operations
        with patch.object(workflow_engine.backup_manager, 'create_backup') as mock_backup, \
             patch('subprocess.run') as mock_subprocess:
            
            mock_backup.return_value = "/backup/path"
            mock_subprocess.return_value = Mock(returncode=0)
            
            result = workflow_engine.ai_component_pipeline(
                temp_component_file, "TestComponent", "Add error handling"
            )
            
            assert isinstance(result, WorkflowResult)
            
            # Check that the file was modified
            with open(temp_component_file, 'r') as f:
                content = f.read()
                assert "AI Workflow" in content or "error handling" in content.lower()
    
    def test_workflow_error_handling(self, config):
        """Test workflow error handling"""
        workflow_engine = AIWorkflowEngine(config)
        
        # Test with nonexistent file
        result = workflow_engine.ai_component_pipeline(
            "/nonexistent/file.py", "TestComponent", "Test prompt"
        )
        
        assert isinstance(result, WorkflowResult)
        assert result.success is False
        assert len(result.error_log) > 0
    
    def test_workflow_caching(self, config, temp_component_file):
        """Test workflow caching behavior"""
        workflow_engine = AIWorkflowEngine(config)
        
        # Mock external dependencies
        with patch.object(workflow_engine.backup_manager, 'create_backup') as mock_backup, \
             patch('subprocess.run') as mock_subprocess:
            
            mock_backup.return_value = "/backup/path"
            mock_subprocess.return_value = Mock(returncode=0)
            
            # First call
            result1 = workflow_engine.ai_component_pipeline(
                temp_component_file, "TestComponent", "Test prompt"
            )
            
            # Second call should use cache for research and analysis
            result2 = workflow_engine.ai_component_pipeline(
                temp_component_file, "TestComponent", "Test prompt"
            )
            
            assert isinstance(result1, WorkflowResult)
            assert isinstance(result2, WorkflowResult)
            
            # Both should complete (success or failure doesn't matter for this test)
            assert result1.component_path == temp_component_file
            assert result2.component_path == temp_component_file


if __name__ == "__main__":
    pytest.main([__file__])