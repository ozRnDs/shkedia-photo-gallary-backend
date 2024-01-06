function updateChild(){
    engine_selector_DOM = document.getElementById("engine_selector")
    
    // Get the selected engine_type
    const selected_engine_option = engine_selector_DOM.options[engine_selector_DOM.selectedIndex];

    // Get the value of the selected option
    const selected_engine = selected_engine_option.value;
       
    const collection_selector_DOM = document.getElementById('collection_selector');

    var selected_option = false
    for (var i = 0; i < collection_selector_DOM.options.length; i++) {
        const parent_name = collection_selector_DOM.options[i].getAttribute("engine_name")
        if (parent_name==selected_engine || parent_name==""){
            collection_selector_DOM.options[i].style.display = 'block';
            if (!selected_option){
                collection_selector_DOM.value = collection_selector_DOM.options[i].value
                selected_option=true
            }
        }else{
            collection_selector_DOM.options[i].style.display = 'none';
        }
        
      }
}

updateChild()

function launchCollection(){

    engine_selector_DOM = document.getElementById("engine_selector")
    
    // Get the selected engine_type
    const selected_engine = engine_selector_DOM.value
       
    const collection_selector_DOM = document.getElementById('collection_selector');

    var selected_collection = collection_selector_DOM.value

    if (!selected_collection==""){
        selected_collection=`/${selected_collection}`

    }

    const btn = document.getElementById("btn_collection")
    btn.className = "fas fa-spinner fa-spin"

    window.location.href = `/collections/${selected_engine}${selected_collection}/1`;
}

function hideAllOptions() {
    // Get the select element
    

    // Iterate through options and hide them
    for (var i = 0; i < selectElement.options.length; i++) {
      selectElement.options[i].style.display = 'none';
    }
  }