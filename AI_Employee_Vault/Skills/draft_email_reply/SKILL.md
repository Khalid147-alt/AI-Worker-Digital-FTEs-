# Skill: Draft Email Reply

## Purpose
Read an email task from /Needs_Action, understand the context, draft a professional reply, and create an approval request.

## Trigger
Any file in /Needs_Action with `type: email`

## Instructions

1. **Read the email file** in /Needs_Action
2. **Extract key info:**
   - Sender
   - Subject
   - Main request/question
   - Tone (formal/casual)

3. **Check Company_Handbook.md** for reply guidelines:
   - Tone standards
   - Approval requirements
   - Any special rules for this sender

4. **Draft a reply** using this structure:
   ```
   Hi [Name],
   
   [Acknowledge their message]
   [Address their request/question]
   [Provide next steps or timeline]
   [Professional closing]
   
   Best regards,
   [Your name from handbook]
   ```

5. **Create approval file** in /Pending_Approval/:
   ```markdown
   ---
   type: approval_request
   action: send_email
   to: <email>
   subject: Re: <original subject>
   original_file: /Needs_Action/EMAIL_xxx.md
   created: <timestamp>
   expires: <24 hours from now>
   status: pending
   ---
   
   ## Draft Email
   
   [Your drafted reply here]
   
   ## Context
   [Brief summary of why you're sending this]
   
   ## To Approve
   Move this file to /Approved
   
   ## To Reject or Edit
   Move this file to /Rejected, or edit the draft and move to /Approved
   ```

6. **Update original task file:**
   - Change status to `awaiting_approval`
   - Add reference to approval file

7. **Log** in /Logs/YYYY-MM-DD.md:
   ```
   [HH:MM] EMAIL DRAFT: Created reply draft for <sender> | Subject: <subject> | Approval: /Pending_Approval/xxx.md
   ```

## Success Criteria
- Draft email is professional and on-brand
- Approval file created in correct location
- Original task updated with status
- Action logged
