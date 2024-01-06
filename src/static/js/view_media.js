
class BoundingBoxElement{
    constructor(image_id,id, x1, y1, x2, y2){
        this.image_id = image_id
        this.id = id
        this.x1 = x1
        this.x2 = x2
        this.y1 = y1
        this.y2 = y2
        this.show = false
    }

    updateBoundingBoxSize(){
        const image = document.getElementById(this.image_id)
        const boundingBox_DOM = document.getElementById(this.id)
	
        // Get the original image dimensions
        const imageNaturalWidth = image.naturalWidth;
        const imageNaturalHeight = image.naturalHeight;

        // Get the current dimensions of the image
        const imageWidth = image.width;
        const imageHeight = image.height;
    
        const resize_w_factor = imageWidth / imageNaturalWidth
        const resize_h_factor = imageHeight / imageNaturalHeight
    
        // Calculate the bounding box coordinates based on the image size
        const boxLeft = this.x1 * resize_w_factor+12 + 'px';
        const boxTop = this.y1 * resize_h_factor + 'px';
        const boxWidth = (this.x2 - this.x1) * resize_w_factor + 'px';
        const boxHeight = (this.y2 - this.y1) * resize_h_factor + 'px';
    
        // Set the position and size of the bounding box
        boundingBox_DOM.style.left = boxLeft;
        boundingBox_DOM.style.top = boxTop;
        boundingBox_DOM.style.width = boxWidth;
        boundingBox_DOM.style.height = boxHeight;
        boundingBox_DOM.style.position = "absolute";
        boundingBox_DOM.style.border = "1px solid red";
        boundingBox_DOM.style.boxSizing="border-box";
        boundingBox_DOM.style.color="red"
    }

    updateDisplay(){
        const boundingBox_DOM = document.getElementById(this.id)
        if (this.show){
            boundingBox_DOM.style.display = 'none';
        }else{
            boundingBox_DOM.style.display = 'block';
        }
        this.show = !this.show
    }
}

const bounding_boxes_elements = new Map();

function add_boundingbox_element(bboxes_wrapper,bounding_box_element,index) {
    const bbox_wrapper_element = document.getElementById(bboxes_wrapper)
    bbox_wrapper_element.innerHTML += `<div id=${bounding_box_element}> ${index}</div>`
}

function displayBoundingBox(image_id,bounding_box_id,index, x1, y1, x2, y2) {
    if (!bounding_boxes_elements.has(bounding_box_id)){
        add_boundingbox_element("boundingboxes",bounding_box_id,index);
        bounding_boxes_elements.set(bounding_box_id, new BoundingBoxElement(image_id, bounding_box_id,x1,y1,x2,y2))
    }
    const boundingBox = bounding_boxes_elements.get(bounding_box_id)
    // Get the original image dimensions:
	boundingBox.updateBoundingBoxSize()
    boundingBox.updateDisplay()
    const eye_icon_DOM = document.getElementById("eye-"+bounding_box_id)

    eye_icon_DOM.classList.toggle("fa-eye")
    eye_icon_DOM.classList.toggle("fa-eye-slash")
    const currentTitle = eye_icon_DOM.getAttribute('data-bs-title')
    const newTitle = (currentTitle === 'Show') ? 'Show' : 'Hide';
    eye_icon_DOM.setAttribute('data-bs-title', newTitle)
    
  }

function update_displayed_bounding_boxes(){
    bounding_boxes_elements.forEach((bbox_object,bbox_id) =>{
        bbox_object.updateBoundingBoxSize()
    })
  }

function expand_row(row_id){
    row_DOM = document.getElementById(row_id)
    expand_DOC = document.getElementById("toggle-"+row_id)
    row_DOM.classList.toggle("d-none")
    expand_DOC.classList.toggle("fa-caret-right")
    expand_DOC.classList.toggle("fa-caret-down")
}

window.addEventListener('resize', update_displayed_bounding_boxes)

const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))