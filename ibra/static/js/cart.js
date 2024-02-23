// $('.clientname').val(localStorage.getItem('clientname'))
// $('.clientphone').val(localStorage.getItem('clientphone'))
// $('.clientaddress').val(localStorage.getItem('clientaddress'))

$('.loadingscreen').addClass('d-none').removeClass('d-flex');

const updatetotal=()=>{
  t=0
  $('.subtotal').each((i, el)=>{
      t+=parseFloat($(el).text())
  })
  $('.total').text(t.toFixed(2))
  if ($('[name="modpymnt"]').val()=='espece'){
    $('.totalremise').text((t.toFixed(2)*0.95).toFixed(2))
  }else{
    $('.totalremise').text(t.toFixed(2))
  }
  $('.ttt').text(t.toFixed(2))
}


const clearstorage =()=>{
  // clear localstorage
  localStorage.removeItem('products')
  localStorage.removeItem('productsdetails')
  // clear table
  $('.cart-table__body').empty()
  //$('.prdctslist').empty()
  $('.commanditems').text(0)
  updatetotal()
}

const validercmnd=(clientid)=>{
  // $('.loadingscreen').removeClass('d-none').addClass('d-flex');

  holder=$('.cmndholder')
  notesorder = localStorage.getItem('notesorder')
  console.log(notesorder)
  commande=[]
  holder.each((i, el)=>{
      ref=$(el).attr('ref')
      id=$(el).attr('id')
      remise=$(el).attr('remise')
      n=$(el).attr('n')
      total=$(el).attr('total')
      price=$(el).attr('price')
      qty=parseInt($(el).find('.qtyholder').text())
      cmd=ref+':'+n+':'+qty+':'+price+':'+id+':'+remise+':'+total
      commande.push(cmd)
  })
  let cmndfromclient=$('.cmndfromclient').val()
  console.log(commande, $('.total').text(), cmndfromclient, clientid)
  $.ajax({
      url: '/commande',
      type: 'POST',
      data: {
          'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
          'commande': commande,
          'notesorder': notesorder,
          'client':clientid,
          'total':$('.total').text(),
          'modpymnt':$('[name="modpymnt"]').val(),
          'modlvrsn':$('[name="modlvrsn"]').val(),
          'clientname':$('.clientname').val(),
          'cmndfromclient':$('.cmndfromclient').val(),
          'clientphone':$('.clientphone').val(),
          'clientaddress':$('.clientaddress').val(),
          'totalremise':parseFloat($('.totalremise').text())
      },

      success: function(data){

          $('select').val(0)
          $('.modes').removeClass('border-danger')
          $('.cmndholder').remove()
          clearstorage()
          $('.valider').prop('disabled', true)
          $('.fromclient').prop('disabled', true)
          localStorage.removeItem('notesorder')
          alertify.success('Commande envoyé')
          $.post('products/notifyadmin', {
            'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val()
          },
          (data)=>{
            console.log('notify admin')
          })
          // go to thank you 
          // if representant
          if (cmndfromclient=='true'){

            window.location.href='/clientdashboar'
          }
          else{

            window.location.href='/ordersforeach'
          }
          // if client

          // window.location.href='/catalogpage'
      },
      error:(err)=>{
          $('.loadingscreen').removeClass('d-none').addclass('d-flex');

          alertify.error(err)
      }
  })
}


function cancelproduct(event, id){
  alertify.confirm('Supprimer?', function(){
    $.get('/removeitemfromcart', {'productid':id}, (data)=>{
      $('.commanditems').html(parseInt($('.commanditems').html())-1)
    })
    $(event.target).parent().parent().remove();
    //updatetotal()
    // remove from local storage
    //products=JSON.parse(localStorage.getItem('products'))
    // using splice
    //let dx=products.indexOf(id)
    //console.log(dx)
    //products.splice(dx, 1)
    //localStorage.setItem('products', JSON.stringify(products))
    // remove from local storage
    //productsdetails=JSON.parse(localStorage.getItem('productsdetails'))
    //productsdetails.splice(dx, 1)
    //localStorage.setItem('productsdetails', JSON.stringify(productsdetails))
    //$('.commanditems').text(products.length)
    // check if cart is empty
    //if (products.length==0){
    //    $('.valider').prop('disabled', true)
    //}
  })
}
//get items from local storage
const loadpdcts=()=>{
  //products=JSON.parse(localStorage.getItem('productsdetails'))
  $('.loadingcartitems').addClass('d-none')
  $.get('/getitemsincart', (data)=>{
    console.log(data.items)
  //   $('tbody').append(`
  //        <tr class="cmndholder" ref="${ref}" n="${n}" id="${id}" remise="${remise}" total=${tt} price=${pr}>
  //        
  //        <td class="">
  //          <a src="${img}" data-toggle="modal" data-target="#imagedisplaymodal" class="imagedisplaybtn" imgsrc="${img}">${ref.toUpperCase()}</a>
  //        </td>
  //        <td class="">
  //          <strong>${n.toUpperCase()}</strong>
  //        </td>
  //        <td class="" data-title="Price">
  //        <small class="priceholder" price=${pr}>${pr}</small>
  //        </td>
  //        <td>${remise}%</td>
  //        <td class=" qtyholder" data-title="Quantity">
  //          ${qty}
  //          
  //        </td>
  //        
  //        <td>
  //          <button class="btn btn-danger" onclick="cancelproduct(event, ${id})">
  //            X
  //          </button>
  //        </td>
  //      </tr>
  //        `)
  })
  //if (products && products.length){
  //    $('.valider').prop('disabled', false)
  //    $('.fromclient').prop('disabled', false)
  //    ttt=0
  //    for (i of products){
  //        let [ref, n, ctg, qty, pr, tt, img, remise, id]=i
  //        ttt+=parseFloat(tt)

  //        $('tbody').append(`
  //        <tr class="cmndholder" ref="${ref}" n="${n}" id="${id}" remise="${remise}" total=${tt} price=${pr}>
  //        
  //        <td class="">
  //          <a src="${img}" data-toggle="modal" data-target="#imagedisplaymodal" class="imagedisplaybtn" imgsrc="${img}">${ref.toUpperCase()}</a>
  //        </td>
  //        <td class="">
  //          <strong>${n.toUpperCase()}</strong>
  //        </td>
  //        <td class="" data-title="Price">
  //        <small class="priceholder" price=${pr}>${pr}</small>
  //        </td>
  //        <td>${remise}%</td>
  //        <td class=" qtyholder" data-title="Quantity">
  //          ${qty}
  //          
  //        </td>
  //        
  //        <td>
  //          <button class="btn btn-danger" onclick="cancelproduct(event, ${id})">
  //            X
  //          </button>
  //        </td>
  //      </tr>
  //        `)
          // $('.input-number').customNumber();
          // $("input[name=qtytosub]").each((i, el)=>{
          //     $(el).on('change', ()=>{
          //         v=$(el).val()
          //         price=parseFloat($(el).parent().parent().parent().find('.priceholder').text())
          //         subt=price*v
          //         // find the subtotal cell
          //         $(el).parent().parent().parent().find('.subtotal').text(subt.toFixed(2))
          //         updatetotal()
          //     }
          // )})
  //    }
  //    $('.ttt').text(ttt.toFixed(2))
  //    $('.total').text(ttt.toFixed(2))
  //    return
  //}
}

