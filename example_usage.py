# """
# Example of how to use the logging decorator with your existing methods.
# Apply @track_method to create, confirm, cancel methods.
# """
#
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from utils.logging_decorator import track_method
#
#
# class TransferViewExample:
#     """Example showing how to apply the decorator to your methods."""
#
#     @track_method('create')
#     def create_transfer(self, request):
#         """Create transfer with logging."""
#         if request.method == 'POST':
#             form = CreateTransferForm(request.POST)
#             if form.is_valid():
#                 transfer = form.save()
#                 return redirect('transfer_success', transfer_id=transfer.id)
#         else:
#             form = CreateTransferForm()
#
#         return render(request, 'transfers/create.html', {'form': form})
#
#     @track_method('confirm')
#     def confirm_transfer(self, request):
#         """Confirm transfer with logging."""
#         if request.method == 'POST':
#             form = ConfirmTransferForm(request.POST)
#             if form.is_valid():
#                 transfer = form.transfer
#                 transfer.state = Transfer.State.CONFIRMED
#                 transfer.save()
#                 messages.success(request, 'Transfer confirmed successfully')
#                 return redirect('transfer_detail', transfer_id=transfer.id)
#         else:
#             form = ConfirmTransferForm()
#
#         return render(request, 'transfers/confirm.html', {'form': form})
#
#     @track_method('cancel')
#     def cancel_transfer(self, request):
#         """Cancel transfer with logging."""
#         if request.method == 'POST':
#             form = CancelTransferForm(request.POST)
#             if form.is_valid():
#                 transfer = form.transfer
#                 transfer.state = Transfer.State.CANCELLED
#                 transfer.save()
#                 messages.info(request, 'Transfer cancelled')
#                 return redirect('transfer_list')
#         else:
#             form = CancelTransferForm()
#
#         return render(request, 'transfers/cancel.html', {'form': form})
#
#
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
#
#
# @api_view(['POST'])
# @track_method('create_api')
# def create_transfer_api(request):
#     """API endpoint with logging."""
#     # Your API logic here
#     return Response({'status': 'created'})
