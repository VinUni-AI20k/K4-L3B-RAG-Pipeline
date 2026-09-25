import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
const root="C:/Users/ADMIN/Documents/PRJ/K4-L3B-RAG-Pipeline";
const skill="C:/Users/ADMIN/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
const build=path.join(root,".pptx_build"), out=path.join(root,"deliverables");
await fs.mkdir(build,{recursive:true}); await fs.mkdir(out,{recursive:true});
const {resolvePresentationFont}=await import(pathToFileURL(path.join(skill,"container_tools/artifact_tool_utils.mjs")).href);
const font=resolvePresentationFont({fontFamily:"Arial"}), W=1280, H=720;
const C={bg:"#07172B",bg2:"#0B2038",bg3:"#102A46",white:"#F6FAFF",muted:"#B7C9DA",cyan:"#54D8E8",cyan2:"#22B8CC",violet:"#A99BFF",line:"#23415E"};
const p=Presentation.create({slideSize:{width:W,height:H}});
function rect(s,x,y,w,h,fill,r=0,stroke="none",sw=0){return s.shapes.add({geometry:r?"roundRect":"rect",position:{left:x,top:y,width:w,height:h},fill,line:{style:"solid",fill:stroke,width:sw},...(r?{borderRadius:r}:{})});}
function line(s,x1,y1,x2,y2,color=C.line,width=2){return s.shapes.add({geometry:"line",position:{left:x1,top:y1,width:x2-x1,height:y2-y1},fill:"none",line:{style:"solid",fill:color,width}});}
function txt(s,text,x,y,w,h,size,color=C.white,bold=false,align="left",valign="middle"){
 const sh=s.shapes.add({geometry:"textbox",position:{left:x,top:y,width:w,height:h},fill:"none",line:{style:"solid",fill:"none",width:0}});
 sh.text=text; sh.text.style={typeface:font,fontSize:size,bold,color,alignment:align,verticalAlignment:valign,wrap:"square",autoFit:"shrinkText",insets:{left:0,right:0,top:0,bottom:0},lineSpacing:1}; return sh;
}
function base(s,title,n){s.background.fill=C.bg;txt(s,"IELTS WRITING  /  RAG",72,38,470,28,16,C.cyan,true);txt(s,String(n).padStart(2,"0"),1170,38,40,28,16,C.muted,true,"right");if(title)txt(s,title,72,88,1130,70,48,C.white,true);}
function note(s,text){s.speakerNotes.textFrame.setText(text);}

// Slide 1 — title
{
 const s=p.slides.add();s.background.fill=C.bg;rect(s,0,0,16,H,C.cyan);rect(s,862,0,418,H,C.bg2);
 txt(s,"IELTS WRITING  /  RAG",78,64,540,32,18,C.cyan,true);
 txt(s,"Hỏi đáp có\nnguồn kiểm chứng",78,176,760,188,62,C.white,true);
 txt(s,"Trợ lý truy xuất tài liệu và trả lời kèm trích dẫn",82,402,720,72,28,C.muted);
 txt(s,"TÀI LIỆU",900,236,250,35,18,C.muted,true);rect(s,900,284,190,9,C.line,5);rect(s,900,284,136,9,C.cyan,5);
 txt(s,"EVIDENCE",900,335,250,35,18,C.muted,true);rect(s,900,383,190,9,C.line,5);rect(s,900,383,166,9,C.violet,5);
 txt(s,"CÂU TRẢ LỜI  [S1]",900,434,300,35,18,C.cyan,true);
 txt(s,"30 câu hỏi đánh giá  ·  5 trang nguồn",82,604,650,32,20,C.muted);
 note(s,"Giới thiệu Ask IELTS Writing: truy xuất bằng chứng từ corpus đã thu thập và sinh câu trả lời có trích dẫn. Corpus benchmark hiện gồm 5 trang chuẩn hóa; golden set 30 câu hỏi tiếng Anh.");
}
// Slide 2 — scope & data
{
 const s=p.slides.add();base(s,"Phạm vi & dữ liệu",2);
 txt(s,"HỎI ĐÁP TRONG IELTS WRITING",74,185,520,34,18,C.cyan,true);
 txt(s,"Task 1/2  ·  tiêu chí  ·  band descriptors",74,229,520,74,27,C.white,true);
 txt(s,"NGUỒN HIỆN CÓ",74,341,270,32,18,C.muted,true);txt(s,"5",72,384,190,124,100,C.cyan,true);txt(s,"trang Markdown",76,514,270,36,24,C.white);
 line(s,430,190,430,560,C.line,2);
 txt(s,"GOLDEN SET",492,185,380,34,18,C.cyan,true);txt(s,"30",488,284,310,142,118,C.white,true);txt(s,"câu hỏi",495,425,300,44,28,C.muted);txt(s,"3 nhóm thử thách",495,489,360,42,23,C.white,true);
 line(s,875,190,875,560,C.line,2);
 txt(s,"10 + 10 + 10",924,278,300,68,37,C.violet,true);
 txt(s,"từ khóa  ·  diễn đạt lại\nnhiều ràng buộc",926,357,300,105,24,C.white);
 txt(s,"Câu hỏi benchmark bằng tiếng Anh",926,494,300,54,18,C.muted);
 note(s,"Golden set: 30 câu, chia đều BM25-targeted, semantic paraphrase và multi-constraint. Benchmark retrieval dùng câu hỏi tiếng Anh phù hợp ngôn ngữ corpus.");
}
// Slide 3 — architecture
{
 const s=p.slides.add();base(s,"Kiến trúc RAG",3);
 txt(s,"Từ tài liệu nguồn đến câu trả lời có thể kiểm chứng",74,164,1000,44,25,C.muted);
 const centers=[145,392,639,886,1133], labels=[["01","Nguồn","IELTS + bài viết"],["02","Chuẩn hóa","Markdown"],["03","Lập chỉ mục","ChromaDB + BM25"],["04","Truy xuất","Dense + RRF"],["05","Trả lời","LLM + [S#]"]];
 for(let i=0;i<centers.length;i++){
  const circ=s.shapes.add({geometry:"ellipse",position:{left:centers[i]-39,top:286,width:78,height:78},fill:i===4?C.violet:C.bg3,line:{style:"solid",fill:i===4?C.violet:C.cyan2,width:2}});
  circ.text=labels[i][0];circ.text.style={typeface:font,fontSize:24,bold:true,color:C.white,alignment:"center",verticalAlignment:"middle",autoFit:"shrinkText",insets:{left:0,right:0,top:0,bottom:0}};
  if(i<centers.length-1){line(s,centers[i]+50,325,centers[i+1]-56,325,C.cyan2,3);txt(s,"›",centers[i+1]-72,302,34,44,42,C.cyan,true,"center");}
  txt(s,labels[i][1],centers[i]-108,398,216,44,24,C.white,true,"center");
  txt(s,labels[i][2],centers[i]-108,447,216,54,19,C.muted,false,"center");
 }
 txt(s,"Chunk theo heading  ·  tối đa 1.200 ký tự  ·  không overlap",75,584,1100,38,21,C.cyan,true,"center");
 note(s,"Luồng: thu thập -> chuẩn hóa Markdown -> chunk và lập chỉ mục -> semantic + lexical retrieval -> RRF -> grounded generation. Chunking mới giới hạn 1200 ký tự, 0 overlap, giữ breadcrumb heading. Vector index lưu trong ChromaDB.");
}
// Slide 4 — retrieval
{
 const s=p.slides.add();base(s,"Truy xuất: hai tín hiệu, một thứ hạng",4);
 txt(s,"SEMANTIC",90,190,300,35,18,C.cyan,true);txt(s,"Dense",90,238,300,58,42,C.white,true);txt(s,"Tìm đoạn gần nghĩa",90,308,320,42,24,C.muted);txt(s,"Cosine similarity",90,357,320,32,19,C.muted);
 txt(s,"+",447,264,100,70,58,C.violet,true,"center");
 txt(s,"TỪ KHÓA",575,190,300,35,18,C.cyan,true);txt(s,"BM25",575,238,300,58,42,C.white,true);txt(s,"Khớp thuật ngữ cụ thể",575,308,350,42,24,C.muted);txt(s,"Lexical ranking",575,357,320,32,19,C.muted);
 line(s,92,430,1185,430,C.line,2);txt(s,"RRF  k=60",92,462,300,52,32,C.violet,true);txt(s,"→",390,460,90,54,38,C.cyan,true,"center");txt(s,"Top 5 đoạn liên quan",490,462,500,52,32,C.white,true);
 txt(s,"Embedding mặc định pipeline: BAAI/bge-m3",92,574,750,38,21,C.muted);txt(s,"Benchmark: all-mpnet-base-v2",92,615,750,30,18,C.violet);
 note(s,"RRF gộp hai danh sách xếp hạng với k=60, xuất top 5. Embedding production mặc định BAAI/bge-m3; benchmark retrieval hiện dùng sentence-transformers/all-mpnet-base-v2. Metric benchmark chưa đại diện chính xác cho BGE-M3.");
}
// Slide 5 — grounded generation
{
 const s=p.slides.add();base(s,"Câu trả lời có nguồn",5);
 txt(s,"CÂU HỎI",76,192,210,32,17,C.cyan,true);txt(s,"Task 2 chiếm bao nhiêu\nđiểm Writing?",76,238,330,115,34,C.white,true);
 txt(s,"→",408,260,90,56,42,C.violet,true,"center");line(s,512,193,512,508,C.line,2);
 txt(s,"BẰNG CHỨNG TRUY XUẤT",560,192,430,32,17,C.cyan,true);txt(s,"“Task 2 is worth two thirds.”",560,242,590,80,29,C.white);txt(s,"[S1]  IELTS Writing Test Resources",560,334,560,34,19,C.muted,true);
 line(s,76,424,1180,424,C.line,2);txt(s,"TRẢ LỜI",76,462,180,30,17,C.cyan,true);txt(s,"Task 2 chiếm 2/3 tổng điểm Writing.  [S1]",76,508,1080,64,31,C.white,true);txt(s,"Không đủ bằng chứng → từ chối an toàn",76,621,900,34,20,C.violet,true);
 note(s,"Ví dụ dựa trên evidence trong golden dataset Q01. LLM mặc định deepseek-flash; câu trả lời chỉ dùng context truy xuất và dùng citation [S#]. Nếu nguồn không xác minh được, hệ thống từ chối an toàn. Streamlit hiển thị câu trả lời và nguồn.");
}
// Slide 6 — evaluation
{
 const s=p.slides.add();base(s,"Kết quả truy xuất",6);
 txt(s,"30 câu hỏi  ·  5 trang nguồn  ·  Hit@k = tìm thấy chunk chứa evidence",74,158,1120,38,22,C.muted);
 const values=[["Phương thức","Hit@1","Hit@3","Hit@5","MRR@5"],["BM25","0,567","0,867","0,900","0,712"],["Dense","0,500","0,667","0,767","0,587"],["Hybrid (RRF)","0,667","0,867","0,900","0,764"]];
 const t=s.tables.add({rows:4,columns:5,left:74,top:226,width:1132,height:300,values});
 t.borders.assign({style:"solid",fill:C.line,width:1});
 for(let r=0;r<4;r++)for(let c=0;c<5;c++){const cell=t.getCell(r,c);cell.fill=r===0?C.bg3:r===3?"#142F4C":C.bg2;cell.text.style={typeface:font,fontSize:r===0?21:27,bold:r===0||r===3,color:r===0?C.cyan:C.white,alignment:c===0?"left":"center",verticalAlignment:"middle",autoFit:"shrinkText",insets:{left:12,right:12,top:8,bottom:8}};}
 txt(s,"Hybrid dẫn đầu ở Hit@1 và MRR@5",76,555,730,48,30,C.cyan,true);txt(s,"Hit@5 bằng BM25",810,559,360,40,24,C.white,true,"right");
 txt(s,"Đo truy xuất evidence, không đo độ đúng câu trả lời LLM.",76,626,1080,28,18,C.muted);
 note(s,"Nguồn: group_project/evaluation/RETRIEVAL_COMPARISON.md và golden_dataset.json. Chunking theo heading, tối đa 1200 ký tự, không overlap. Benchmark 30 câu tiếng Anh trên 5 trang. Dense model benchmark all-mpnet-base-v2; pipeline mặc định BAAI/bge-m3. Hit@k/MRR@5 đo truy xuất evidence, không đo chất lượng generation. Hybrid Hit@5 = BM25 = 0.900; Hybrid MRR@5 cao nhất = 0.764.");
}
const candidate=path.join(build,"candidate.pptx"), previews=[];
for(let i=0;i<p.slides.items.length;i++){const blob=await p.export({slide:p.slides.items[i],format:"png",scale:1});const file=path.join(build,"slide-"+(i+1)+".png");await fs.writeFile(file,new Uint8Array(await blob.arrayBuffer()));previews.push(file);}
await (await PresentationFile.exportPptx(p)).save(candidate);
console.log(JSON.stringify({candidate,previews,font,slides:p.slides.items.length}));


