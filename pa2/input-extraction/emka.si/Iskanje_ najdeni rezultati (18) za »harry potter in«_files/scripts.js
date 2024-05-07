(function(){var __sections__={};(function(){for(var i=0,s=document.getElementById("sections-script").getAttribute("data-sections").split(",");i<s.length;i++)__sections__[s[i]]=!0})(),function(){if(__sections__.footer)try{class LocalizationForm extends HTMLElement{constructor(){super(),this.elements={input:this.querySelector('input[name="locale_code"], input[name="country_code"]'),button:this.querySelector("button"),panel:this.querySelector(".disclosure__list-wrapper")},this.elements.button.addEventListener("click",this.openSelector.bind(this)),this.elements.button.addEventListener("focusout",this.closeSelector.bind(this)),this.addEventListener("keyup",this.onContainerKeyUp.bind(this)),this.querySelectorAll("a").forEach(item=>item.addEventListener("click",this.onItemClick.bind(this)))}hidePanel(){this.elements.button.setAttribute("aria-expanded","false"),this.elements.panel.setAttribute("hidden",!0)}onContainerKeyUp(event){event.code.toUpperCase()==="ESCAPE"&&(this.hidePanel(),this.elements.button.focus())}onItemClick(event){event.preventDefault();const form=this.querySelector("form");this.elements.input.value=event.currentTarget.dataset.value,form&&form.submit()}openSelector(){this.elements.button.focus(),this.elements.panel.toggleAttribute("hidden"),this.elements.button.setAttribute("aria-expanded",(this.elements.button.getAttribute("aria-expanded")==="false").toString())}closeSelector(event){const shouldClose=event.relatedTarget&&event.relatedTarget.nodeName==="BUTTON";(event.relatedTarget===null||shouldClose)&&this.hidePanel()}}customElements.define("localization-form",LocalizationForm)}catch(e){console.error(e)}}(),function(){if(__sections__["product-recommendations"])try{class ProductRecommendations extends HTMLElement{constructor(){super();const handleIntersection=(entries,observer)=>{entries[0].isIntersecting&&(observer.unobserve(this),fetch(this.dataset.url).then(response=>response.text()).then(text=>{const html=document.createElement("div");html.innerHTML=text;const recommendations=html.querySelector("product-recommendations");recommendations&&recommendations.innerHTML.trim().length&&(this.innerHTML=recommendations.innerHTML),html.querySelector(".grid__item")&&this.classList.add("product-recommendations--loaded")}).catch(e=>{console.error(e)}))};new IntersectionObserver(handleIntersection.bind(this),{rootMargin:"0px 0px 200px 0px"}).observe(this)}}customElements.define("product-recommendations",ProductRecommendations)}catch(e){console.error(e)}}()})();
//# sourceMappingURL=/cdn/shop/t/31/compiled_assets/scripts.js.map?82718=
