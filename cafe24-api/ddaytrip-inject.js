(function(){
'use strict';
if(!location.pathname.includes('/reservation/detail'))return;

// ============================================================
// 상품별 설정 (product_no 기준으로 추가/수정)
// ============================================================
var PRODUCTS = {
  '133': {
    minPeople:  '2인',
    transport:  '항공 포함',
    departure:  '인천 / 김해',
    departureOptions: ['인천 출발', '김해 출발', '대구 출발', '청주 출발'],
  },
  // 새 상품 추가 예시:
  // '200': {
  //   minPeople:  '4인',
  //   transport:  '항공 포함',
  //   departure:  '인천',
  //   departureOptions: ['인천 출발'],
  // },
};
// 기본값 (위 목록에 없는 상품에 적용)
var DEFAULT_CFG = {
  minPeople:  '2인',
  transport:  '항공 포함',
  departure:  '인천',
  departureOptions: ['인천 출발'],
};
var productNo = new URLSearchParams(location.search).get('product_no') || '';
// ============================================================

// Swiper CSS
var l=document.createElement('link');
l.rel='stylesheet';
l.href='https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css';
document.head.appendChild(l);

// Swiper JS 로드 후 메인 실행 (DOM이 완전히 로드된 후 CFG 읽기)
var s=document.createElement('script');
s.src='https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js';
s.onload=function(){runInject();};
document.head.appendChild(s);

function runInject(){
// 상품 상세에 삽입된 설정값 우선 사용, 없으면 PRODUCTS 맵, 그것도 없으면 기본값
var CFG = (function(){
  try {
    var el = document.getElementById('ddaytrip-config');
    if(el) return JSON.parse(el.textContent);
  } catch(e){}
  return PRODUCTS[productNo] || DEFAULT_CFG;
})();

// ===== CSS =====
var style=document.createElement('style');
style.textContent=`
body.ddaytrip-detail-page{background:#f0f2f5}
.ddaytrip-detail-wrap{max-width:720px;margin:0 auto;background:#fff;font-family:'Apple SD Gothic Neo','Noto Sans KR',sans-serif}
.dd-gallery{position:relative;background:#000;width:100%}
.dd-gallery .swiper{height:300px}
@media(min-width:480px){.dd-gallery .swiper{height:380px}}
.dd-gallery img{width:100%;height:100%;object-fit:cover;opacity:.92}
.dd-gallery-counter{position:absolute;bottom:12px;right:16px;background:rgba(0,0,0,.55);color:#fff;font-size:.78rem;padding:4px 10px;border-radius:50px;z-index:10}
.dd-gallery-btn{position:absolute;top:50%;transform:translateY(-50%);background:rgba(0,0,0,.45);color:#fff;border:none;width:36px;height:36px;border-radius:50%;font-size:1rem;display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:10}
.dd-gallery-btn.prev{left:12px}.dd-gallery-btn.next{right:12px}
.dd-summary{background:#fff;padding:20px 16px 16px;border-bottom:1px solid #e5e7eb}
.dd-badge{display:inline-block;background:#e8f5e9;color:#1a7d3b;font-size:.78rem;font-weight:700;padding:4px 12px;border-radius:50px;margin-bottom:8px}
.dd-title{font-size:1.3rem;font-weight:900;color:#1a1a1a;margin-bottom:6px;line-height:1.3}
.dd-subtitle{font-size:.82rem;color:#6b7280;margin-bottom:16px}
.dd-specs{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#e5e7eb;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden}
.dd-spec{background:#fff;padding:12px;display:flex;flex-direction:column;gap:4px}
.dd-spec dt{font-size:.72rem;color:#6b7280;font-weight:600}
.dd-spec dd{font-size:.9rem;font-weight:700;color:#1a1a1a}
.dd-spec-price{color:#ff6b00!important;font-size:1.1rem!important}
.dd-booking{background:#fff;padding:20px 16px;margin-top:8px}
.dd-booking h2{font-size:1.05rem;font-weight:800;margin-bottom:14px;color:#1a1a1a}
.dd-booking-form{display:flex;flex-direction:column;gap:12px;margin-bottom:18px}
.dd-form-row{display:flex;align-items:center;gap:10px}
.dd-form-label{font-size:.85rem;font-weight:600;min-width:60px;flex-shrink:0}
.dd-form-input{flex:1;border:1.5px solid #e5e7eb;border-radius:8px;padding:10px 12px;font-size:.9rem;outline:none;font-family:inherit;color:#1a1a1a}
.dd-form-input:focus{border-color:#1a7d3b}
.dd-people-select{display:flex;align-items:center;gap:10px;flex:1}
.dd-people-btn{width:34px;height:34px;border:1.5px solid #e5e7eb;border-radius:50%;font-size:1.2rem;display:flex;align-items:center;justify-content:center;cursor:pointer;font-family:inherit;transition:all .2s;background:#fff}
.dd-people-btn:hover{border-color:#1a7d3b;color:#1a7d3b}
.dd-people-count{font-size:1.1rem;font-weight:700;min-width:24px;text-align:center}
.dd-price-box{background:#f7f8fa;border-radius:12px;padding:16px;margin-bottom:16px}
.dd-price-row{display:flex;justify-content:space-between;font-size:.88rem;color:#6b7280;margin-bottom:8px}
.dd-price-total{display:flex;justify-content:space-between;align-items:center;border-top:1px solid #e5e7eb;padding-top:12px;margin-top:8px;font-weight:700;font-size:.95rem}
.dd-total-num{font-size:1.3rem;font-weight:900;color:#ff6b00}
.dd-price-note{font-size:.72rem;color:#9ca3af;margin-top:6px}
.dd-book-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.dd-btn-phone,.dd-btn-kakao,.dd-btn-reserve{padding:13px;border-radius:12px;font-size:.9rem;font-weight:700;text-align:center;cursor:pointer;transition:opacity .2s;font-family:inherit;text-decoration:none;display:block;border:none}
.dd-btn-phone{background:#fff;border:1.5px solid #1a7d3b;color:#1a7d3b}
.dd-btn-kakao{background:#fee500;color:#3c1e1e}
.dd-btn-reserve{grid-column:1/-1;background:#1a7d3b;color:#fff;font-size:1rem}
.dd-tabs{display:flex;background:#fff;border-bottom:2px solid #e5e7eb;position:sticky;top:0;z-index:100;overflow-x:auto;scrollbar-width:none;margin-top:8px}
.dd-tabs::-webkit-scrollbar{display:none}
.dd-tab{padding:14px 18px;font-size:.88rem;font-weight:600;color:#6b7280;white-space:nowrap;border-bottom:3px solid transparent;cursor:pointer;transition:all .2s;font-family:inherit;background:none;border-left:none;border-right:none;border-top:none}
.dd-tab.active{color:#1a7d3b;border-bottom-color:#1a7d3b}
.dd-section{background:#fff;padding:24px 16px;margin-top:8px}
.dd-section.bg-gray{background:#f7f8fa}
.dd-section-title{font-size:1.05rem;font-weight:800;color:#1a1a1a;margin-bottom:6px}
.dd-section-sub{font-size:.8rem;color:#6b7280;margin-bottom:16px}
.dd-orig-detail{font-size:.88rem;line-height:1.6;color:#374151}
.dd-orig-detail img{max-width:100%;height:auto;border-radius:8px;margin:8px 0}
.dd-orig-detail table{width:100%;border-collapse:collapse;margin:8px 0;font-size:.82rem}
.dd-orig-detail td,.dd-orig-detail th{border:1px solid #e5e7eb;padding:8px 10px;text-align:left}
.dd-orig-detail th{background:#1a7d3b;color:#fff}
.dd-inc-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px}
.dd-inc-card{border-radius:12px;padding:14px}
.dd-inc-yes{background:#e8f5e9;border:1px solid #a5d6a7}
.dd-inc-no{background:#fff3e0;border:1px solid #ffcc80}
.dd-inc-title{font-size:.88rem;font-weight:700;margin-bottom:10px}
.dd-inc-list{display:flex;flex-direction:column;gap:6px;padding:0;list-style:none}
.dd-inc-list li{font-size:.8rem;color:#374151;padding-left:10px;position:relative;line-height:1.4}
.dd-inc-list li::before{content:'·';position:absolute;left:0;font-weight:700}
.dd-notice-box{border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;margin-top:12px}
.dd-notice-header{background:#f7f8fa;padding:12px 16px;font-size:.88rem;font-weight:700;border-bottom:1px solid #e5e7eb}
.dd-notice-body{padding:12px 16px;list-style:none}
.dd-notice-body li{font-size:.8rem;color:#374151;padding-left:12px;position:relative;line-height:1.5;margin-bottom:4px}
.dd-notice-body li::before{content:'•';position:absolute;left:0;color:#ff6b00}
.dd-accordion{border:1px solid #e5e7eb;border-radius:12px;overflow:hidden}
.dd-acc-item{border-bottom:1px solid #e5e7eb}
.dd-acc-item:last-child{border-bottom:none}
.dd-acc-toggle{width:100%;display:flex;justify-content:space-between;align-items:center;padding:14px 16px;font-size:.88rem;font-weight:600;background:#fff;cursor:pointer;font-family:inherit;border:none;text-align:left;transition:background .2s}
.dd-acc-toggle:hover{background:#f7f8fa}
.dd-acc-arrow{font-size:.75rem;color:#9ca3af;transition:transform .3s}
.dd-acc-item.open .dd-acc-arrow{transform:rotate(180deg)}
.dd-acc-content{display:none;padding:12px 16px 16px;background:#f7f8fa;font-size:.82rem;color:#374151;line-height:1.6}
.dd-acc-item.open .dd-acc-content{display:block}
.dd-cancel-table{width:100%;border-collapse:collapse;font-size:.82rem}
.dd-cancel-table th{background:#1a7d3b;color:#fff;padding:8px 12px;text-align:left;font-weight:700}
.dd-cancel-table td{padding:8px 12px;border-bottom:1px solid #e5e7eb;background:#fff}
.dd-cancel-table tr:nth-child(even) td{background:#f7f8fa}
.dd-sticky-bar{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:720px;display:grid;grid-template-columns:1fr 1fr;background:#fff;border-top:1px solid #e5e7eb;box-shadow:0 -4px 16px rgba(0,0,0,.1);z-index:500}
.dd-sticky-btn{padding:14px 8px;font-size:.85rem;font-weight:700;text-align:center;border:none;cursor:pointer;font-family:inherit;text-decoration:none;display:block}
.dd-sticky-phone{background:#fff;color:#1a7d3b;border-right:1px solid #e5e7eb}
.dd-sticky-kakao{background:#fee500;color:#3c1e1e;border-right:1px solid #e5e7eb}
.dd-sticky-reserve{background:#1a7d3b;color:#fff;font-size:.95rem}
.dd-modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:2000;display:none;align-items:flex-end}
.dd-modal-overlay.open{display:flex}
.dd-modal{background:#fff;width:100%;max-width:720px;margin:0 auto;border-radius:20px 20px 0 0;max-height:90vh;overflow-y:auto;animation:ddSlideUp .35s ease}
@keyframes ddSlideUp{from{transform:translateY(100%)}to{transform:translateY(0)}}
.dd-modal-header{display:flex;justify-content:space-between;align-items:center;padding:18px 20px;border-bottom:1px solid #e5e7eb;position:sticky;top:0;background:#fff;z-index:1}
.dd-modal-header h3{font-size:1rem;font-weight:800}
.dd-modal-close{font-size:1.2rem;color:#9ca3af;cursor:pointer;background:none;border:none;font-family:inherit}
.dd-modal-body{padding:20px}
.dd-form-group{display:flex;flex-direction:column;gap:6px;margin-bottom:14px}
.dd-form-group label{font-size:.85rem;font-weight:600}
.dd-form-group input,.dd-form-group select,.dd-form-group textarea{border:1.5px solid #e5e7eb;border-radius:8px;padding:10px 12px;font-size:.9rem;font-family:inherit;outline:none;width:100%;box-sizing:border-box}
.dd-form-group input:focus,.dd-form-group select:focus,.dd-form-group textarea:focus{border-color:#1a7d3b}
.dd-agree{display:flex;align-items:center;gap:8px;font-size:.82rem;color:#6b7280;cursor:pointer;margin-bottom:16px}
.dd-btn-submit{background:#1a7d3b;color:#fff;padding:14px;border-radius:12px;font-size:1rem;font-weight:700;font-family:inherit;cursor:pointer;border:none;width:100%}
body.ddaytrip-detail-page{padding-bottom:64px}
body.ddaytrip-detail-page .reservation_area{display:none!important}
`;
document.head.appendChild(style);

// ===== 페이지 구성 =====
document.body.classList.add('ddaytrip-detail-page');

var titleEl=document.querySelector('.reservation_prod_name');
var priceEl=document.querySelector('.reservation_product_price');
var productTitle=titleEl?titleEl.innerText.trim():document.title;
var productPrice=priceEl?priceEl.innerText.trim():'';
var basePrice=parseInt((productPrice||'0').replace(/[^0-9]/g,''),10)||0;

// 이미지 수집
var thumbImgs=[];
var bigImg=document.querySelector('#pcProdThumb img.BigImage');
if(bigImg)thumbImgs.push(bigImg.src);
document.querySelectorAll('#pcProdThumb img.ThumbImage').forEach(function(img){
  var s=img.src.replace('/extra/small/','/extra/big/').replace('/product/small/','/product/big/');
  if(thumbImgs.indexOf(s)===-1)thumbImgs.push(s);
});
if(!thumbImgs.length)thumbImgs=['https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=800'];

// 포함/불포함 파싱
var incYes=[],incNo=[],notices=[];
var contEl=document.querySelector('#prdDetail .cont');
if(contEl){
  var ft=contEl.innerText||'';
  var ym=ft.match(/[✓☑]\s*포함내역([\s\S]*?)(?:[×✗☒]\s*불포함|$)/);
  if(ym)ym[1].split('\n').forEach(function(l){l=l.replace(/^[\s◆▶•\t]+/,'').trim();if(l&&l.length>2&&!l.includes('포함내역'))incYes.push(l);});
  var nm=ft.match(/[×✗☒]\s*불포함내역([\s\S]*?)(?:[✎✏]|\d+일차|여행일정|일정은|$)/);
  if(nm)nm[1].split('\n').forEach(function(l){l=l.replace(/^[\s◆▶•\t]+/,'').trim();if(l&&l.length>2&&!l.includes('불포함내역'))incNo.push(l);});
  var nt=ft.match(/[✎✏]\s*중요 안내사항([\s\S]*?)(?:\d+일차|여행일정|일정은|$)/);
  if(nt)nt[1].split('\n').forEach(function(l){l=l.replace(/^[\s※\t]+/,'').trim();if(l&&l.length>3)notices.push(l);});
}
if(!incYes.length)incYes=['상품 상세 내용을 확인해 주세요'];
if(!incNo.length)incNo=['상품 상세 내용을 확인해 주세요'];

var detailCont=document.querySelector('#prdDetail .cont');
var detailHTML=detailCont?detailCont.innerHTML:'';

function fmtPrice(p,n){if(!p)return '문의요망';return (p*n).toLocaleString('ko-KR')+'원~';}

var slides=thumbImgs.map(function(s){return '<div class="swiper-slide"><img src="'+s+'" loading="lazy"/></div>';}).join('');
var yesLi=incYes.map(function(t){return '<li>'+t+'</li>';}).join('');
var noLi=incNo.map(function(t){return '<li>'+t+'</li>';}).join('');
var notLi=notices.length?notices.map(function(t){return '<li>'+t+'</li>';}).join(''):'<li>상세 내용을 확인해 주세요</li>';

var html=
'<div class="ddaytrip-detail-wrap">'+
  '<div class="dd-gallery">'+
    '<div class="swiper dd-gallery-swiper"><div class="swiper-wrapper">'+slides+'</div></div>'+
    '<div class="dd-gallery-counter" id="ddGalCounter">1 / '+thumbImgs.length+'</div>'+
    '<button class="dd-gallery-btn prev" id="ddGalPrev">&#8592;</button>'+
    '<button class="dd-gallery-btn next" id="ddGalNext">&#8594;</button>'+
  '</div>'+
  '<div class="dd-summary">'+
    '<span class="dd-badge">✈️ 골프 패키지</span>'+
    '<h1 class="dd-title">'+productTitle+'</h1>'+
    '<p class="dd-subtitle">해외골프여행 맞춤전문 디데이트립</p>'+
    '<dl class="dd-specs">'+
      '<div class="dd-spec"><dt>💰 최저가 (1인)</dt><dd class="dd-spec-price">'+( productPrice||'문의요망')+'</dd></div>'+
      '<div class="dd-spec"><dt>👥 최소인원</dt><dd>'+CFG.minPeople+'</dd></div>'+
      '<div class="dd-spec"><dt>✈️ 교통편</dt><dd>'+CFG.transport+'</dd></div>'+
      '<div class="dd-spec"><dt>📍 출발지</dt><dd>'+CFG.departure+'</dd></div>'+
    '</dl>'+
  '</div>'+
  '<div class="dd-booking">'+
    '<h2>📋 예약 문의</h2>'+
    '<div class="dd-book-actions">'+
      '<a href="tel:010-4109-0510" class="dd-btn-phone">📞 전화 예약</a>'+
      '<a href="http://pf.kakao.com/_kkBKG/chat" target="_blank" class="dd-btn-kakao">💬 카카오</a>'+
    '</div>'+
  '</div>'+
  '<nav class="dd-tabs" id="ddTabs">'+
    '<button class="dd-tab active" data-target="ddItinerary">상세일정</button>'+
    '<button class="dd-tab" data-target="ddIncludes">포함/불포함</button>'+
    '<button class="dd-tab" data-target="ddCourseInfo">골프장/숙박</button>'+
    '<button class="dd-tab" data-target="ddTips">참고사항</button>'+
    '<button class="dd-tab" data-target="ddReviews">후기</button>'+
  '</nav>'+
  '<div class="dd-section" id="ddItinerary"><div class="dd-section-title">📅 상세 일정</div><p class="dd-section-sub">항공사 및 현지 사정에 따라 변경될 수 있습니다</p><div class="dd-orig-detail">'+detailHTML+'</div></div>'+
  '<div class="dd-section bg-gray" id="ddIncludes"><div class="dd-section-title">포함 / 불포함 사항</div><div class="dd-inc-grid"><div class="dd-inc-card dd-inc-yes"><div class="dd-inc-title">✅ 포함</div><ul class="dd-inc-list">'+yesLi+'</ul></div><div class="dd-inc-card dd-inc-no"><div class="dd-inc-title">❌ 불포함</div><ul class="dd-inc-list">'+noLi+'</ul></div></div><div class="dd-notice-box"><div class="dd-notice-header">⚠️ 중요 안내사항</div><ul class="dd-notice-body">'+notLi+'</ul></div></div>'+
  '<div class="dd-section" id="ddCourseInfo"><div class="dd-section-title">⛳ 골프장 &amp; 🏨 숙박 정보</div><div class="dd-orig-detail" id="ddInfoOrig"></div></div>'+
  '<div class="dd-section bg-gray" id="ddTips"><div class="dd-section-title">여행 전 참고사항</div><div class="dd-accordion"><div class="dd-acc-item open"><button class="dd-acc-toggle"><span>예약 취소료 규정</span><span class="dd-acc-arrow">▼</span></button><div class="dd-acc-content"><table class="dd-cancel-table"><thead><tr><th>취소 시점</th><th>취소 수수료</th></tr></thead><tbody><tr><td>출발 31일 전</td><td>없음</td></tr><tr><td>출발 30~21일 전</td><td>10%</td></tr><tr><td>출발 20~11일 전</td><td>20%</td></tr><tr><td>출발 10~8일 전</td><td>30%</td></tr><tr><td>출발 7~1일 전</td><td>50%</td></tr><tr><td>출발 당일</td><td>100%</td></tr></tbody></table></div></div><div class="dd-acc-item"><button class="dd-acc-toggle"><span>예약 시 유의사항</span><span class="dd-acc-arrow">▼</span></button><div class="dd-acc-content"><ul style="padding-left:4px"><li style="margin-bottom:6px">예약 확정 후 여권 정보 제출 필요</li><li style="margin-bottom:6px">예약금 입금 후 예약 확정</li><li style="margin-bottom:6px">항공 좌석 상황에 따라 일정 변경 가능</li><li>여권 유효기간 6개월 이상 필요</li></ul></div></div><div class="dd-acc-item"><button class="dd-acc-toggle"><span>해외 긴급 연락처</span><span class="dd-acc-arrow">▼</span></button><div class="dd-acc-content"><ul style="padding-left:4px"><li style="margin-bottom:6px">010-4109-0510 (성차민 팀장)</li><li style="margin-bottom:6px">010-4667-2301 (김남희 팀장)</li><li>현지 가이드: 예약 확정 후 안내</li></ul></div></div></div></div>'+
  '<div class="dd-section" id="ddReviews"><div class="dd-section-title">💬 예약 후기</div><p style="text-align:center;color:#9ca3af;padding:20px;font-size:.85rem">등록된 후기가 없습니다.<br><a href="/board/product/list.html?board_no=4" style="color:#1a7d3b;font-weight:700">전체 후기 보러가기</a></p></div>'+
'</div>'+
'<div class="dd-sticky-bar"><a href="tel:010-4109-0510" class="dd-sticky-btn dd-sticky-phone">📞 전화상담</a><a href="http://pf.kakao.com/_kkBKG/chat" target="_blank" class="dd-sticky-btn dd-sticky-kakao">💬 카카오</a></div>';

var target=document.querySelector('.reservation_area');
if(!target)return;
var w=document.createElement('div');
w.innerHTML=html;
target.parentNode.insertBefore(w,target);
target.style.display='none';

// 골프장/숙박 정보 주입
var pi=document.querySelector('#prdInfo .cont');
var io=document.getElementById('ddInfoOrig');
if(pi&&io)io.innerHTML=pi.innerHTML;

// ===== 이벤트 =====
var galSwiper=new Swiper('.dd-gallery-swiper',{loop:false,speed:400,on:{slideChange:function(){var c=document.getElementById('ddGalCounter');if(c)c.textContent=(this.realIndex+1)+' / '+this.slides.length;}}});
var gp=document.getElementById('ddGalPrev');var gn=document.getElementById('ddGalNext');
if(gp)gp.addEventListener('click',function(){galSwiper.slidePrev();});
if(gn)gn.addEventListener('click',function(){galSwiper.slideNext();});

var people=2;
function updPrice(){
  var pc=document.getElementById('ddPeopleCount');var pl=document.getElementById('ddPeopleLabel');var tp=document.getElementById('ddTotalPrice');
  if(pc)pc.textContent=people;if(pl)pl.textContent=people+'명';
  if(tp)tp.textContent=basePrice?(basePrice*people).toLocaleString('ko-KR')+'원~':'문의요망';
}
var mb=document.getElementById('ddMinus');var pb=document.getElementById('ddPlus');
if(mb)mb.addEventListener('click',function(){if(people>1){people--;updPrice();}});
if(pb)pb.addEventListener('click',function(){if(people<30){people++;updPrice();}});

var d=new Date();d.setDate(d.getDate()+14);
var di=document.getElementById('ddDepartDate');
if(di){di.min=new Date().toISOString().split('T')[0];di.value=d.toISOString().split('T')[0];}

document.querySelectorAll('.dd-tab').forEach(function(tab){
  tab.addEventListener('click',function(){
    document.querySelectorAll('.dd-tab').forEach(function(t){t.classList.remove('active');});
    tab.classList.add('active');
    var sec=document.getElementById(tab.dataset.target);
    if(sec)window.scrollTo({top:sec.getBoundingClientRect().top+window.scrollY-56,behavior:'smooth'});
  });
});

document.querySelectorAll('.dd-acc-toggle').forEach(function(btn){
  btn.addEventListener('click',function(){
    var item=btn.closest('.dd-acc-item');var isOpen=item.classList.contains('open');
    document.querySelectorAll('.dd-acc-item').forEach(function(i){i.classList.remove('open');});
    if(!isOpen)item.classList.add('open');
  });
});


}// end runInject
})();
