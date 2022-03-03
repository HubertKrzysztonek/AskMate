document.querySelector("#accept").onclick = function (){
    const h3 = document.querySelector("#answer");

    console.log(h3.style);
    h3.style.color = "yellow";
}