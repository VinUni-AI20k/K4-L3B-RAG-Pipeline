import path from "node:path";
import { pathToFileURL } from "node:url";
const root="C:/Users/ADMIN/Documents/PRJ/K4-L3B-RAG-Pipeline";
const skill="C:/Users/ADMIN/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
process.env.RUNTIME_NODE_MODULES="C:/Users/ADMIN/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,"container_tools/artifact_tool_utils.mjs")).href);
const staging=path.join(root,".pptx_build");
const finalPath=path.join(root,"deliverables","IELTS_Writing_RAG_6_Slides.pptx");
const result=await finalizePresentation({
 workspaceDir:root,
 candidatePath:path.join(staging,"candidate.pptx"),
 finalPath,
 pythonExecutable:"C:/Users/ADMIN/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",
 integrityValidatorPath:path.join(skill,"container_tools/inspect_presentation_package_integrity.py"),
 layoutValidatorPath:path.join(skill,"container_tools/inspect_presentation_layout_geometry.py"),
 layoutArgs:["--expected-slide-size-emu","12192000,6858000","--validate-bullet-geometry","--validate-heading-fit","--require-native-table-slide","6"],
 explicitTotalSlideCount:6,
 requiredNativeTableOwnerSlides:[6],
 fontPolicy:{basis:"design",families:["Arial"]},
 verifyArtifactToolImport:true,
 receiptPath:path.join(staging,"validation.json")
});
console.log(JSON.stringify(result));

